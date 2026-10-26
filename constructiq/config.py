"""Central settings for ConstructIQ."""

APP_NAME = "ConstructIQ"
APP_TAGLINE = "Multimodal Construction Intelligence Platform"
APP_VERSION = "1.0.0"

# Gemini models tried in order (free-tier friendly).
GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
]

# Severity scale used across the app.
SEVERITY_LEVELS = ["Low", "Medium", "High", "Critical"]

# Standards the analysis prompts are grounded in.
STANDARDS = {
    "OSHA 29 CFR 1926": "Site safety, PPE and fall protection",
    "IS 456:2000": "Plain and reinforced concrete code of practice (India)",
    "IS 875": "Design loads, including wind loads (India)",
    "IS 4926": "Ready-mixed concrete and curing practice (India)",
}

IMAGE_TYPES = ["jpg", "jpeg", "png"]
MAX_IMAGE_SIDE = 1600  # images are downscaled before being sent to Gemini