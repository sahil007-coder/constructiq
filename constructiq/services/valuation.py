"""Budget, material and asset-value estimates in INR.

All rates are indicative planning assumptions, not quotes. Adjust the tables
below to match local market data before relying on the numbers.
"""
from __future__ import annotations

from urllib.parse import quote

STRUCTURE_TYPES = ["Residential Apartment", "Independent House / Villa",
                   "Commercial Office", "Industrial / Warehouse"]
TIERS = ["Tier 1", "Tier 2", "Tier 3"]
TIER_HELP = {"Tier 1": "Metros (Mumbai, Delhi NCR, Bengaluru, Chennai ...)",
             "Tier 2": "Cities such as Pune, Jaipur, Indore, Nagpur ...",
             "Tier 3": "Smaller cities and towns"}

# Construction cost, INR per sq ft of built-up area (Tier 2 baseline).
BUILD_RATE = {"Residential Apartment": 1800, "Independent House / Villa": 2200,
              "Commercial Office": 2600, "Industrial / Warehouse": 1500}
TIER_COST_FACTOR = {"Tier 1": 1.25, "Tier 2": 1.00, "Tier 3": 0.85}
CONTINGENCY = 0.08  # approvals, site overheads and contingency on top of build cost

# Completed-asset market value, INR per sq ft of built-up area.
MARKET_RATE = {
    "Tier 1": {"Residential Apartment": 9000, "Independent House / Villa": 11000,
               "Commercial Office": 12000, "Industrial / Warehouse": 4500},
    "Tier 2": {"Residential Apartment": 5000, "Independent House / Villa": 6500,
               "Commercial Office": 7000, "Industrial / Warehouse": 2800},
    "Tier 3": {"Residential Apartment": 3000, "Independent House / Villa": 4000,
               "Commercial Office": 4200, "Industrial / Warehouse": 1800},
}
LAND_SHARE = 0.35  # share of completed value attributed to land (held from day one)

# Rule-of-thumb material needs per sq ft of built-up area.
CEMENT_BAGS_PER_SQFT = 0.40          # 50 kg bags
STEEL_KG_PER_SQFT = {"Residential Apartment": 4.0, "Independent House / Villa": 4.0,
                     "Commercial Office": 5.0, "Industrial / Warehouse": 3.5}

MILESTONES = [
    ("Site prep & foundation", 0, 20),
    ("Superstructure (columns, slabs)", 20, 55),
    ("Masonry, MEP rough-in", 55, 75),
    ("Finishing", 75, 95),
    ("Handover & snagging", 95, 100),
]


def format_inr(amount: float) -> str:
    """Format rupees as Lakhs / Crores, e.g. ₹1.25 Cr, ₹48.20 L."""
    amount = float(amount)
    sign = "-" if amount < 0 else ""
    a = abs(amount)
    if a >= 1e7:
        return f"{sign}₹{a / 1e7:,.2f} Cr"
    if a >= 1e5:
        return f"{sign}₹{a / 1e5:,.2f} L"
    return f"{sign}₹{a:,.0f}"


def current_milestone(completion_pct: float) -> str:
    for name, start, end in MILESTONES:
        if completion_pct < end:
            return name
    return MILESTONES[-1][0]


def estimate(structure: str, sqft: float, tier: str, completion_pct: float) -> dict:
    if structure not in BUILD_RATE or tier not in TIER_COST_FACTOR:
        raise ValueError("Unknown structure type or tier.")
    if sqft <= 0:
        raise ValueError("Built-up area must be greater than zero.")
    completion_pct = max(0.0, min(100.0, float(completion_pct)))
    frac = completion_pct / 100

    build_cost = sqft * BUILD_RATE[structure] * TIER_COST_FACTOR[tier]
    budget = build_cost * (1 + CONTINGENCY)
    capex = budget * frac

    completed_value = sqft * MARKET_RATE[tier][structure]
    current_value = completed_value * (LAND_SHARE + (1 - LAND_SHARE) * frac)

    cement_total = sqft * CEMENT_BAGS_PER_SQFT
    steel_total_t = sqft * STEEL_KG_PER_SQFT[structure] / 1000
    return {
        "inputs": {"structure": structure, "built_up_sqft": sqft, "tier": tier,
                   "completion_pct": completion_pct},
        "total_budget_inr": round(budget),
        "capex_incurred_inr": round(capex),
        "balance_to_spend_inr": round(budget - capex),
        "completed_asset_value_inr": round(completed_value),
        "current_market_value_inr": round(current_value),
        "cement_bags_total": round(cement_total),
        "cement_tonnes_total": round(cement_total * 0.05, 1),
        "steel_tonnes_total": round(steel_total_t, 1),
        "cement_bags_used": round(cement_total * frac),
        "steel_tonnes_used": round(steel_total_t * frac, 1),
        "milestone": current_milestone(completion_pct),
    }


def rendering_prompt(structure: str, tier: str, sqft: float, completion_pct: float) -> str:
    """Text prompt for a conceptual 3D architectural rendering."""
    stage = ("under construction with exposed concrete frame and scaffolding"
             if completion_pct < 70 else
             "nearly complete with finishing work visible" if completion_pct < 100
             else "completed and landscaped")
    setting = {"Tier 1": "dense metropolitan Indian city", "Tier 2": "growing Indian city",
               "Tier 3": "small Indian town"}[tier]
    return (f"Conceptual 3D architectural rendering of a {structure.lower()}, about "
            f"{int(sqft):,} sq ft built-up area, {stage}, set in a {setting}, "
            "realistic daylight, modern Indian architecture, high detail")


def pollinations_url(prompt: str, seed: int = 7) -> str:
    return (f"https://image.pollinations.ai/prompt/{quote(prompt)}"
            f"?width=1024&height=640&nologo=true&seed={seed}")
