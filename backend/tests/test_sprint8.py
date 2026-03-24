"""Tests for Sprint 8 — Rate Cards, Health, Security"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rate_cards import get_rate_cards, get_tier, TIER_ORDER


# ─── Rate Cards ───

def test_free_tier_exists():
    tier = get_tier("free")
    assert tier is not None
    assert tier["price"] == "$0"

def test_pro_tier_exists():
    tier = get_tier("pro")
    assert tier is not None
    assert tier["price"] == "$19"

def test_team_tier_exists():
    tier = get_tier("team")
    assert tier is not None
    assert tier["price"] == "$49"

def test_enterprise_tier_exists():
    tier = get_tier("enterprise")
    assert tier is not None
    assert tier["price"] == "Custom"

def test_free_tier_has_features():
    tier = get_tier("free")
    assert len(tier["features"]) >= 3

def test_pro_tier_highlighted():
    tier = get_tier("pro")
    assert tier["highlighted"] is True

def test_free_tier_not_highlighted():
    tier = get_tier("free")
    assert tier["highlighted"] is False

def test_get_rate_cards_returns_all():
    cards = get_rate_cards()
    assert len(cards) == 4

def test_tier_order():
    assert TIER_ORDER == ["free", "pro", "team", "enterprise"]

def test_all_tiers_have_cta():
    for tier_name in TIER_ORDER:
        tier = get_tier(tier_name)
        assert "cta" in tier
        assert len(tier["cta"]) > 0

def test_invalid_tier_returns_none():
    assert get_tier("platinum") is None


# ─── Health Endpoint (via app) ───

def test_app_loads_all_modules():
    """Verify all Sprint 1-8 modules import correctly."""
    from app import app
    assert app is not None

def test_health_route_exists():
    from app import app
    rules = [r.rule for r in app.url_map.iter_rules()]
    assert "/api/health" in rules

def test_rate_cards_route_exists():
    from app import app
    rules = [r.rule for r in app.url_map.iter_rules()]
    assert "/api/rate-cards" in rules


# ─── API Endpoint Count ───

def test_total_api_endpoints():
    """Verify we have all expected v2 endpoints."""
    from app import app
    api_routes = [r.rule for r in app.url_map.iter_rules() if "/api/" in r.rule]
    # We should have 50+ endpoints after all sprints
    assert len(api_routes) >= 50, f"Only {len(api_routes)} API routes found"
