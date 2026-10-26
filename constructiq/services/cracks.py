"""Crack diagnostics: prompt, validation, IS 456 width check and demo result."""
from __future__ import annotations

from typing import Any

from ..config import SEVERITY_LEVELS

DEFECT_TYPES = ["Hairline", "Settlement", "Structural Shear", "Thermal Expansion", "Spalling"]

# IS 456:2000 cl. 35.3.2: surface crack width should generally not exceed 0.3 mm
# (0.2 mm in severe exposure) for reinforced concrete members.
IS456_LIMIT_MM = 0.3
IS456_SEVERE_LIMIT_MM = 0.2

PROMPT = """You are a structural engineer inspecting a photo of a concrete or
masonry surface. Classify the defect and recommend repairs in line with
IS 456:2000 and good Indian site practice. Do not claim certainty from a photo;
recommend a physical inspection when severity is High or Critical.

Return ONLY a JSON object with exactly these keys:
{
  "defect_type": "Hairline" | "Settlement" | "Structural Shear" | "Thermal Expansion" | "Spalling",
  "estimated_width_mm": number,
  "root_causes": [str],
  "recommended_repairs": [str],   // e.g. epoxy injection, structural re-grouting
  "urgency": {"level": "Low|Medium|High|Critical", "timeframe": str},
  "summary": str
}"""

DEMO = {
    "defect_type": "Structural Shear",
    "estimated_width_mm": 0.8,
    "root_causes": [
        "Diagonal tension near the support, suggesting shear stress above capacity",
        "Possible shortage of shear stirrups or excess concentrated load",
    ],
    "recommended_repairs": [
        "Low-viscosity epoxy injection to seal and bond the crack",
        "Structural re-grouting of the affected zone",
        "Install crack monitors (tell-tales) and review the load path with a structural engineer",
    ],
    "urgency": {"level": "High", "timeframe": "Inspect within 1 week; restrict loading until cleared"},
    "summary": "Demonstration result: sample findings, not based on your photo. "
               "Add a Gemini API key in the sidebar for a real analysis.",
}


def width_check(width_mm: float) -> dict:
    """Compare a crack width with the IS 456 limits."""
    if width_mm <= IS456_SEVERE_LIMIT_MM:
        return {"within_limit": True, "message": f"{width_mm:.2f} mm is within the IS 456 limits (0.2 mm severe / 0.3 mm general)."}
    if width_mm <= IS456_LIMIT_MM:
        return {"within_limit": True, "message": f"{width_mm:.2f} mm is within the general IS 456 limit of 0.3 mm but above the 0.2 mm limit for severe exposure."}
    return {"within_limit": False, "message": f"{width_mm:.2f} mm exceeds the IS 456 general limit of 0.3 mm."}


def _as_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [value]
    return [str(v) for v in (value or []) if str(v).strip()]


def normalize(raw: dict) -> dict:
    defect = str(raw.get("defect_type", "")).strip().title()
    lookup = {d.lower(): d for d in DEFECT_TYPES}
    defect = lookup.get(defect.lower(), "Hairline")

    try:
        width = max(0.0, round(float(raw.get("estimated_width_mm", 0)), 2))
    except (TypeError, ValueError):
        width = 0.0

    urg = raw.get("urgency") or {}
    if isinstance(urg, str):
        urg = {"level": urg, "timeframe": ""}
    level = str(urg.get("level", "")).strip().title()
    level = {"Moderate": "Medium", "Immediate": "Critical"}.get(level, level)
    if level not in SEVERITY_LEVELS:
        level = "Critical" if width > 3 else "High" if width > 1 else "Medium" if width > 0.3 else "Low"

    out = {
        "defect_type": defect,
        "estimated_width_mm": width,
        "root_causes": _as_list(raw.get("root_causes")),
        "recommended_repairs": _as_list(raw.get("recommended_repairs")),
        "urgency": {"level": level, "timeframe": str(urg.get("timeframe", ""))},
        "summary": str(raw.get("summary", "")),
    }
    out["is456_check"] = width_check(width)
    return out


def demo_result() -> dict:
    return normalize(DEMO)
