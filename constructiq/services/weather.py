"""Weather-aware site advisories (rule based, works offline)."""
from __future__ import annotations

CONDITIONS = ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"]

ADVISORIES = {
    "Normal": {
        "level": "Low",
        "headline": "Normal working conditions",
        "alerts": [
            {"title": "Routine start-of-shift checks", "severity": "Low",
             "actions": ["Hold the toolbox talk and confirm PPE at site entry.",
                         "Inspect scaffolds, ladders and lifting tackle before use.",
                         "Keep access routes and edges clear and barricaded."],
             "standard": "OSHA 29 CFR 1926"},
        ],
    },
    "High Wind": {
        "level": "Critical",
        "headline": "High wind: suspend lifting and secure the site",
        "alerts": [
            {"title": "Suspend crane operations", "severity": "Critical",
             "actions": ["Stop lifts when wind reaches the limit in the crane manufacturer's load chart.",
                         "Stop lifting large-surface loads (sheets, panels, shuttering) earlier than that.",
                         "Park and weathervane tower cranes as per the manufacturer's instructions.",
                         "Keep people clear of the crane's fall zone."],
             "standard": "OSHA 1926.1417; IS 875 (Part 3) wind loads"},
            {"title": "Work at height", "severity": "High",
             "actions": ["Stop work on scaffolds, roof edges and open floors.",
                         "Check scaffold ties and bracing; remove sheeting and loose boards."],
             "standard": "OSHA 1926.451"},
            {"title": "Loose materials and temporary works", "severity": "Medium",
             "actions": ["Tie down or store formwork, sheets, bricks and bags.",
                         "Check hoardings, temporary props and tower-crane tie-ins after the wind drops."],
             "standard": "IS 456 cl. 11 (formwork)"},
        ],
    },
    "Heavy Rain": {
        "level": "High",
        "headline": "Heavy rain: protect people, electrics and fresh concrete",
        "alerts": [
            {"title": "Electrical hazard mitigation", "severity": "Critical",
             "actions": ["De-energise temporary supply to wet areas and isolate damaged cables.",
                         "Confirm earth-leakage protection (RCCB/ELCB) works; test before restart.",
                         "Keep cable joints off the ground and panels covered and locked.",
                         "Only competent electricians restore supply."],
             "standard": "OSHA 1926 Subpart K; IS 732 / National Electrical Code"},
            {"title": "Excavations and shoring", "severity": "High",
             "actions": ["Keep people out of trenches until a competent person re-inspects the sides.",
                         "Dewater and divert run-off away from excavations.",
                         "Check shoring and keep spoil heaps back from edges."],
             "standard": "OSHA 1926 Subpart P"},
            {"title": "Concrete and masonry", "severity": "Medium",
             "actions": ["Postpone pours in heavy rain; cover fresh concrete and reinforcement.",
                         "Do not let rain wash cement out of fresh concrete.",
                         "Re-check formwork and props for softening ground."],
             "standard": "IS 456 cl. 13 (concreting)"},
            {"title": "Slips and falls", "severity": "Medium",
             "actions": ["Clear mud from walkways and ladders; stop work on wet scaffold boards."],
             "standard": "OSHA 1926.451"},
        ],
    },
    "Extreme Heat": {
        "level": "High",
        "headline": "Extreme heat: protect workers and cure concrete properly",
        "alerts": [
            {"title": "Concrete curing protocol", "severity": "High",
             "actions": ["Pour early morning or evening; shade and cool aggregates and mixing water.",
                         "Start curing as soon as the surface can take it: wet hessian, ponding or curing compound.",
                         "Keep exposed surfaces continuously damp for at least 7 days (10 days with mineral admixtures or blended cements).",
                         "Watch for plastic shrinkage cracks and fast slump loss; do not add water on site."],
             "standard": "IS 456 cl. 13.5 (curing); IS 7861 (Part 1) hot-weather concreting"},
            {"title": "Heat-illness prevention", "severity": "High",
             "actions": ["Provide shade, drinking water and ORS; schedule rest breaks.",
                         "Move heavy work to cooler hours and rotate crews.",
                         "Know the signs of heat exhaustion and heat stroke; call for medical help early."],
             "standard": "OSHA heat illness guidance (General Duty Clause)"},
            {"title": "Equipment and materials", "severity": "Medium",
             "actions": ["Check hot steel, cylinders and fuel storage; keep in shade.",
                         "Check hydraulic hoses and tyres on plant."],
             "standard": "Site safety plan"},
        ],
    },
}


def advisory_for(condition: str) -> dict:
    if condition not in ADVISORIES:
        raise ValueError(f"Unknown weather condition: {condition}")
    return ADVISORIES[condition]
