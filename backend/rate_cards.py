"""
Rate Cards - GrowthPath v2.0 (Sprint 8)
Display-only pricing tiers for future monetization.
"""

RATE_CARDS = {
    "free": {
        "name": "Free",
        "price": "$0",
        "period": "forever",
        "description": "Get started with basic mock interviews",
        "features": [
            "3 full mock interviews per month",
            "Unlimited Quick Assessments",
            "1 company profile (Google)",
            "Comfort Mode only",
            "Basic ELO tracking",
            "Learning path with AI content",
        ],
        "limitations": [
            "No Interview or Pressure modes",
            "Single company profile",
            "No hiring committee simulation",
        ],
        "cta": "Get Started Free",
        "highlighted": False,
    },
    "pro": {
        "name": "Pro",
        "price": "$19",
        "period": "/month",
        "description": "Serious interview preparation",
        "features": [
            "Unlimited mock interviews",
            "All company profiles (Google, Apple, Amazon, Meta, Netflix)",
            "All modes: Comfort, Interview, Pressure",
            "AI Interviewer with real-time conversation",
            "Hiring committee simulation",
            "Rubric reveal on every question",
            "Pattern mastery tracking with trends",
            "Priority AI response time",
            "Detailed analytics dashboard",
            "Mock interview replay",
        ],
        "limitations": [],
        "cta": "Start Pro Trial",
        "highlighted": True,
    },
    "team": {
        "name": "Team",
        "price": "$49",
        "period": "/user/month",
        "description": "For engineering teams and managers",
        "features": [
            "Everything in Pro",
            "Team dashboards",
            "Promotion readiness reports",
            "Manager view of team progress",
            "Custom company profiles",
            "Bulk user management",
            "Team analytics and benchmarks",
        ],
        "limitations": [],
        "cta": "Contact Sales",
        "highlighted": False,
    },
    "enterprise": {
        "name": "Enterprise",
        "price": "Custom",
        "period": "",
        "description": "For organizations at scale",
        "features": [
            "Everything in Team",
            "SSO / SAML integration",
            "API access",
            "Custom question banks",
            "White-label option",
            "Dedicated support",
            "SLA guarantee",
            "Bulk licensing discounts",
        ],
        "limitations": [],
        "cta": "Contact Sales",
        "highlighted": False,
    },
}

TIER_ORDER = ["free", "pro", "team", "enterprise"]


def get_rate_cards():
    """Return all rate cards in display order."""
    return [RATE_CARDS[tier] for tier in TIER_ORDER]


def get_tier(tier_name):
    """Get a specific tier's details."""
    return RATE_CARDS.get(tier_name.lower())
