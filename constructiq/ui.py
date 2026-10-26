"""Small shared UI helpers for the tabs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Optional

import streamlit as st
from PIL import Image

from . import styles
from .config import IMAGE_TYPES
from .gemini_client import GeminiUnavailable, generate_json, is_live

ROOT = Path(__file__).resolve().parent.parent


def pick_image(key: str, label: str, sample_name: Optional[str] = None) -> Optional[Image.Image]:
    """Upload widget (JPG/PNG) with an optional bundled sample image."""
    upload = st.file_uploader(label, type=IMAGE_TYPES, key=f"{key}_upload")
    sample = ROOT / sample_name if sample_name else None
    use_sample = False
    if sample and sample.exists():
        use_sample = st.checkbox("Use the bundled sample photo instead", key=f"{key}_sample")
    try:
        if upload is not None:
            return Image.open(upload)
        if use_sample:
            return Image.open(sample)
    except Exception:
        styles.notice("That file could not be read as an image. Please upload a JPG or PNG.", "bad")
    return None


def run_analysis(key: str, prompt: str, image: Optional[Image.Image],
                 normalize: Callable[[dict], dict], demo: Callable[[], dict]) -> None:
    """Run Gemini (or the demo) and keep the result in session state."""
    with st.spinner("Analyzing..."):
        if not is_live():
            st.session_state[key] = {"data": demo(), "mode": "demo"}
            return
        try:
            data = normalize(generate_json(prompt, image))
            st.session_state[key] = {"data": data, "mode": "live"}
        except GeminiUnavailable as exc:
            st.session_state[key] = {"data": demo(), "mode": "fallback", "error": str(exc)}


def mode_banner(result: dict) -> None:
    mode = result.get("mode")
    if mode == "demo":
        styles.notice("<b>Demonstration mode:</b> this is a sample result, not an analysis of your image.")
    elif mode == "fallback":
        styles.notice("<b>Gemini could not be reached,</b> so a sample result is shown instead. "
                      "Check your key and try again.", "warn")
        if result.get("error"):
            with st.expander("Technical details (send this if you need help)"):
                st.code(result["error"], language="text")


def json_download(data: dict, filename: str, label: str = "Download JSON report") -> None:
    st.download_button(label, json.dumps(data, indent=2), file_name=filename,
                       mime="application/json", width="stretch")