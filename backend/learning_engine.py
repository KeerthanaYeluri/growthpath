"""
Learning Path Engine.
Generates personalized learning plans from user's tech_stack + interest_areas.
Calculates target dates based on hours_per_day commitment.
"""

from datetime import datetime, timedelta
from topic_catalog import get_all_topics_for_interests, get_total_hours, TOPIC_CATALOG
import storage


def generate_learning_plan(user_id):
    """Generate a learning plan based on user profile."""
    user = storage.get_user(user_id)
    if not user:
        return None, "User not found"

    interest_areas = user.get("interest_areas", [])
    hours_per_day = user.get("hours_per_day", 2.0)

    if not interest_areas:
        return None, "No interest areas selected"

    all_topics = get_all_topics_for_interests(interest_areas)
    if not all_topics:
        return None, "No topics found for selected interests"

    # Calculate target dates
    plan_topics = []
    current_date = datetime.now()
    cumulative_hours = 0

    for topic in all_topics:
        start_date = current_date + timedelta(hours=cumulative_hours / hours_per_day * 24)
        cumulative_hours += topic["estimated_hours"]
        end_date = current_date + timedelta(hours=cumulative_hours / hours_per_day * 24)

        plan_topics.append({
            "topic_id": topic["topic_id"],
            "title": topic["title"],
            "interest_area": topic["interest_area"],
            "description": topic["description"],
            "estimated_hours": topic["estimated_hours"],
            "sequence": topic["sequence"],
            "original_start_date": start_date.strftime("%Y-%m-%d"),
            "original_end_date": end_date.strftime("%Y-%m-%d"),
            "revised_start_date": start_date.strftime("%Y-%m-%d"),
            "revised_end_date": end_date.strftime("%Y-%m-%d"),
            "status": "not_started",
            "dimensions_completed": [],
            "assessment_score": None,
            "assessment_rating": None,
        })

    total_hours = get_total_hours(interest_areas)
    total_days = total_hours / hours_per_day if hours_per_day > 0 else 0

    plan = {
        "user_id": user_id,
        "interest_areas": interest_areas,
        "hours_per_day": hours_per_day,
        "total_estimated_hours": total_hours,
        "total_estimated_days": round(total_days),
        "plan_created_at": datetime.now().isoformat(),
        "expected_completion": (datetime.now() + timedelta(days=total_days)).strftime("%Y-%m-%d"),
        "topics": plan_topics,
    }

    # Save the plan
    storage.save_learning_plan(user_id, plan)
    return plan, None


def get_next_topic(user_id):
    """Get the next topic the user should work on."""
    plan = storage.get_learning_plan(user_id)
    if not plan:
        return None

    for topic in plan.get("topics", []):
        if topic["status"] != "completed":
            return topic
    return None


def mark_dimension_complete(user_id, topic_id, dimension):
    """Mark a content dimension as complete for a topic."""
    plan = storage.get_learning_plan(user_id)
    if not plan:
        return None

    for topic in plan.get("topics", []):
        if topic["topic_id"] == topic_id:
            if dimension not in topic["dimensions_completed"]:
                topic["dimensions_completed"].append(dimension)
            # If all 4 dimensions done, mark topic as ready for assessment
            if len(topic["dimensions_completed"]) >= 4 and topic["status"] != "completed":
                topic["status"] = "content_complete"
            elif len(topic["dimensions_completed"]) > 0 and topic["status"] == "not_started":
                topic["status"] = "in_progress"
            break

    storage.save_learning_plan(user_id, plan)
    return plan


def mark_topic_assessed(user_id, topic_id, score, rating):
    """Mark a topic as assessed with score."""
    plan = storage.get_learning_plan(user_id)
    if not plan:
        return None

    for topic in plan.get("topics", []):
        if topic["topic_id"] == topic_id:
            topic["assessment_score"] = score
            topic["assessment_rating"] = rating
            topic["status"] = "completed"
            break

    storage.save_learning_plan(user_id, plan)
    return plan


def get_plan_progress(user_id):
    """Calculate overall plan progress percentage."""
    plan = storage.get_learning_plan(user_id)
    if not plan:
        return {"progress_pct": 0, "completed": 0, "total": 0}

    topics = plan.get("topics", [])
    if not topics:
        return {"progress_pct": 0, "completed": 0, "total": 0}

    completed = sum(1 for t in topics if t["status"] == "completed")
    in_progress = sum(1 for t in topics if t["status"] in ("in_progress", "content_complete"))

    # Weight: completed = 1.0, in_progress = 0.5
    progress = (completed + in_progress * 0.5) / len(topics) * 100

    return {
        "progress_pct": round(progress),
        "completed": completed,
        "in_progress": in_progress,
        "total": len(topics),
    }
