"""
Adaptive Scheduler.
Recalculates target dates when user is ahead or behind schedule.
Preserves dates when ahead, extends when behind.
"""

from datetime import datetime, timedelta
import storage


def recalculate_schedule(user_id):
    """Recalculate all future dates based on actual progress."""
    plan = storage.get_learning_plan(user_id)
    if not plan:
        return None

    user = storage.get_user(user_id)
    hours_per_day = user.get("hours_per_day", 2.0) if user else 2.0
    topics = plan.get("topics", [])

    now = datetime.now()
    remaining_hours = 0

    # Find the first non-completed topic
    first_incomplete_idx = None
    for i, topic in enumerate(topics):
        if topic["status"] != "completed":
            if first_incomplete_idx is None:
                first_incomplete_idx = i
            remaining_hours += topic["estimated_hours"]

    if first_incomplete_idx is None:
        # All done
        return plan

    # Recalculate dates for remaining topics starting from today
    cumulative_hours = 0
    for i in range(first_incomplete_idx, len(topics)):
        topic = topics[i]
        if topic["status"] == "completed":
            continue

        start_date = now + timedelta(hours=cumulative_hours / hours_per_day * 24)
        cumulative_hours += topic["estimated_hours"]
        end_date = now + timedelta(hours=cumulative_hours / hours_per_day * 24)

        topic["revised_start_date"] = start_date.strftime("%Y-%m-%d")
        topic["revised_end_date"] = end_date.strftime("%Y-%m-%d")

    # Update expected completion
    if hours_per_day > 0:
        total_remaining_days = remaining_hours / hours_per_day
        plan["expected_completion"] = (now + timedelta(days=total_remaining_days)).strftime("%Y-%m-%d")

    storage.save_learning_plan(user_id, plan)
    return plan


def get_schedule_status(user_id):
    """Get schedule status with delay indicators per topic."""
    plan = storage.get_learning_plan(user_id)
    if not plan:
        return []

    now = datetime.now()
    statuses = []

    for topic in plan.get("topics", []):
        original_end = datetime.strptime(topic["original_end_date"], "%Y-%m-%d")
        revised_end = datetime.strptime(topic["revised_end_date"], "%Y-%m-%d")

        delay_days = (revised_end - original_end).days

        if topic["status"] == "completed":
            indicator = "green"
        elif delay_days > 7:
            indicator = "red"
        elif delay_days > 3:
            indicator = "yellow"
        else:
            indicator = "green"

        statuses.append({
            "topic_id": topic["topic_id"],
            "title": topic["title"],
            "original_end_date": topic["original_end_date"],
            "revised_end_date": topic["revised_end_date"],
            "delay_days": delay_days,
            "indicator": indicator,
            "status": topic["status"],
        })

    return statuses
