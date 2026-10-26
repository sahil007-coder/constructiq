import pytest

from constructiq.services import valuation as v


def test_format_inr():
    assert v.format_inr(12_500_000) == "₹1.25 Cr"
    assert v.format_inr(4_820_000) == "₹48.20 L"
    assert v.format_inr(9_500) == "₹9,500"


def test_estimate_basic_numbers():
    e = v.estimate("Residential Apartment", 1000, "Tier 2", 50)
    assert e["total_budget_inr"] == round(1000 * 1800 * 1.08)
    assert e["capex_incurred_inr"] == round(e["total_budget_inr"] * 0.5)
    assert e["cement_bags_total"] == 400
    assert e["steel_tonnes_total"] == 4.0
    assert e["milestone"] == "Superstructure (columns, slabs)"


def test_tier_orders_cost_and_value():
    t1 = v.estimate("Commercial Office", 2000, "Tier 1", 60)
    t3 = v.estimate("Commercial Office", 2000, "Tier 3", 60)
    assert t1["total_budget_inr"] > t3["total_budget_inr"]
    assert t1["current_market_value_inr"] > t3["current_market_value_inr"]


def test_value_grows_with_completion_and_hits_full_value():
    low = v.estimate("Independent House / Villa", 1500, "Tier 2", 0)
    high = v.estimate("Independent House / Villa", 1500, "Tier 2", 100)
    assert low["current_market_value_inr"] < high["current_market_value_inr"]
    assert high["current_market_value_inr"] == high["completed_asset_value_inr"]
    assert high["balance_to_spend_inr"] == 0


def test_completion_is_clamped_and_bad_input_rejected():
    assert v.estimate("Residential Apartment", 1000, "Tier 2", 250)["inputs"]["completion_pct"] == 100
    with pytest.raises(ValueError):
        v.estimate("Residential Apartment", 0, "Tier 2", 10)
    with pytest.raises(ValueError):
        v.estimate("Castle", 1000, "Tier 2", 10)


def test_pollinations_url_is_encoded():
    url = v.pollinations_url(v.rendering_prompt("Commercial Office", "Tier 1", 5000, 80))
    assert url.startswith("https://image.pollinations.ai/prompt/") and " " not in url
