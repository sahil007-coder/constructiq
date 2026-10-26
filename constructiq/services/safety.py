"""Site safety and PPE audit: prompt, validation and demo result."""
from __future__ import annotations

from typing import Any

from ..config import SEVERITY_LEVELS

PPE_ITEMS = {
    "helmet": "Safety helmet",
    "high_vis_vest": "High-visibility vest",
    "safety_boots": "Steel-toe safety boots",
    "safety_harness": "Safety harness / fall arrest",
}
PPE_STATES = ["worn", "missing", "not_visible", "not_applicable"]
STATUSES = ["Compliant", "Needs Attention", "Non-Compliant"]

PROMPT = """You are a construction site safety officer auditing a photo against
OSHA 29 CFR 1926 (PPE, fall protection, scaffolds) and IS 456:2000 (concrete
work, formwork and shoring practice). Be conservative: only report what is
visible. If no workers are visible, say so and mark PPE as "not_visible".

Return ONLY a JSON object with exactly these keys:
{
  "safety_score": integer 0-100 (100 = fully safe),
  "overall_status": "Compliant" | "Needs Attention" | "Non-Compliant",
  "workers_detected": integer,
  "ppe_detection": {
    "helmet": {"status": "worn|missing|not_visible|not_applicable", "note": str},
    "high_vis_vest": {"status": "...", "note": str},
    "safety_boots": {"status": "...", "note": str},
    "safety_harness": {"status": "...", "note": str}
  },
  "hazards": [
    {"description": str, "severity": "Low|Medium|High|Critical",
     "standard": "clause, e.g. OSHA 1926.501 or IS 456 cl. 11", "remedy": str}
  ],
  "summary": str
}"""

DEMO = {
    "safety_score": 54,
    "overall_status": "Non-Compliant",
    "workers_detected": 2,
    "ppe_detection": {
        "helmet": {"status": "worn", "note": "Both workers wear helmets."},
        "high_vis_vest": {"status": "missing", "note": "One worker has no high-visibility vest."},
        "safety_boots": {"status": "not_visible", "note": "Footwear is not clearly visible."},
        "safety_harness": {"status": "missing", "note": "Worker at height without fall arrest."},
    },
    "hazards": [
        {"description": "Worker on elevated platform without fall arrest or guardrail",
         "severity": "Critical", "standard": "OSHA 1926.501 / 1926.451",
         "remedy": "Stop work at height; install guardrails and provide harness with anchor point."},
        {"description": "Missing high-visibility apparel near active work zone",
         "severity": "Medium", "standard": "OSHA 1926.201",
         "remedy": "Issue high-visibility vests and enforce at site entry."},
        {"description": "Props and formwork bracing not clearly secured",
         "severity": "High", "standard": "IS 456:2000 cl. 11 (formwork)",
         "remedy": "Have a site engineer inspect shoring and add bracing before loading."},
    ],
    "summary": "Demonstration result: sample findings, not based on your photo. "
               "Add a Gemini API key in the sidebar for a real analysis.",
}


def _clean_severity(value: Any) -> str:
    text = str(value).strip().title()
    aliases = {"Moderate": "Medium", "Severe": "Critical", "Minor": "Low", "Ok": "Low"}
    text = aliases.get(text, text)
    return text if text in SEVERITY_LEVELS else "Medium"


def normalize(raw: dict) -> dict:
    """Coerce a model reply into the exact schema the UI expects."""
    try:
        score = int(round(float(raw.get("safety_score", 0))))
    except (TypeError, ValueError):
        score = 0
    score = max(0, min(100, score))

    status = str(raw.get("overall_status", "")).strip().title()
    if status not in STATUSES:
        status = "Compliant" if score >= 80 else "Needs Attention" if score >= 55 else "Non-Compliant"

    ppe_in = raw.get("ppe_detection") or {}
    ppe = {}
    for key in PPE_ITEMS:
        item = ppe_in.get(key) or {}
        state = str(item.get("status", "not_visible")).strip().lower().replace(" ", "_")
        ppe[key] = {"status": state if state in PPE_STATES else "not_visible",
                    "note": str(item.get("note", ""))}

    hazards = []
    for h in raw.get("hazards") or []:
        if not isinstance(h, dict) or not h.get("description"):
            continue
        hazards.append({
            "description": str(h["description"]),
            "severity": _clean_severity(h.get("severity")),
            "standard": str(h.get("standard", "")),
            "remedy": str(h.get("remedy", "")),
        })
    hazards.sort(key=lambda h: SEVERITY_LEVELS.index(h["severity"]), reverse=True)

    try:
        workers = max(0, int(raw.get("workers_detected", 0)))
    except (TypeError, ValueError):
        workers = 0

    return {"safety_score": score, "overall_status": status, "workers_detected": workers,
            "ppe_detection": ppe, "hazards": hazards, "summary": str(raw.get("summary", ""))}


def demo_result() -> dict:
    return normalize(DEMO)
