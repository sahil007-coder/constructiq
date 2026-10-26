"""Gemini access with graceful fallback to demonstration mode.

Uses Google's current `google-genai` SDK. The key is never bundled with the app.
It comes from, in order: the sidebar input, Streamlit secrets, then the
GEMINI_API_KEY environment variable.

Every request has a hard timeout and a single attempt, so the app can never
sit on "Contacting Gemini..." for minutes: it either answers or reports why not.
"""
from __future__ import annotations

import json
import os
import re
from typing import Optional

import streamlit as st
from PIL import Image

from .config import GEMINI_MODELS, MAX_IMAGE_SIDE

KEY_STATE = "gemini_api_key"
REQUEST_TIMEOUT_S = 40


class GeminiUnavailable(Exception):
    """Raised when no key is set or every model call failed."""


def get_api_key() -> str:
    key = (st.session_state.get(KEY_STATE) or "").strip()
    if key:
        return key
    try:
        key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:
        key = ""
    return key or os.environ.get("GEMINI_API_KEY", "").strip()


def is_live() -> bool:
    return bool(get_api_key())


def _describe(name: str, exc: Exception) -> str:
    """One readable line per failed model, with the key masked."""
    text = f"{name}: {type(exc).__name__}: {exc}".replace("\n", " ")
    key = get_api_key()
    if key:
        text = text.replace(key, "***")
    return text[:400]


def prepare_image(img: Image.Image) -> Image.Image:
    """Convert to RGB and downscale so uploads stay small and fast."""
    img = img.convert("RGB")
    longest = max(img.size)
    if longest > MAX_IMAGE_SIDE:
        scale = MAX_IMAGE_SIDE / longest
        img = img.resize((int(img.width * scale), int(img.height * scale)))
    return img


def parse_json(text: str) -> dict:
    """Pull a JSON object out of a model reply, tolerating code fences."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            text = text[start : end + 1]
    return json.loads(text)


def _generate(model: str, contents, *, json_mode: bool = False,
              system_instruction: Optional[str] = None, timeout_s: int = REQUEST_TIMEOUT_S) -> str:
    """One Gemini call: single attempt, hard timeout. Returns the reply text."""
    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=get_api_key(),
        http_options=types.HttpOptions(
            timeout=timeout_s * 1000,  # milliseconds
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )
    config = types.GenerateContentConfig(
        temperature=0.2,
        response_mime_type="application/json" if json_mode else None,
        system_instruction=system_instruction,
    )
    reply = client.models.generate_content(model=model, contents=contents, config=config)
    return reply.text or ""


def generate_json(prompt: str, image: Optional[Image.Image] = None) -> dict:
    """Ask Gemini for a JSON object. Raises GeminiUnavailable on any failure."""
    if not is_live():
        raise GeminiUnavailable("No API key supplied.")
    contents = [prompt] if image is None else [prompt, prepare_image(image)]
    errors: list[str] = []
    for name in GEMINI_MODELS:
        try:
            return parse_json(_generate(name, contents, json_mode=True))
        except Exception as exc:  # network, quota, timeout, bad JSON ...
            errors.append(_describe(name, exc))
    raise GeminiUnavailable("\n".join(errors))


def generate_chat(system_prompt: str, history: list[dict], message: str) -> str:
    """Multi-turn chat. history items look like {"role": "user"|"assistant", "content": str}."""
    if not is_live():
        raise GeminiUnavailable("No API key supplied.")
    from google.genai import types

    contents = []
    for turn in history:
        role = "user" if turn["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=turn["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
    errors: list[str] = []
    for name in GEMINI_MODELS:
        try:
            return _generate(name, contents, system_instruction=system_prompt)
        except Exception as exc:
            errors.append(_describe(name, exc))
    raise GeminiUnavailable("\n".join(errors))


def test_connection() -> tuple[bool, str]:
    """Send a tiny prompt to each model and report exactly what happened."""
    if not is_live():
        return False, "No API key entered."
    lines, ok = [], False
    for name in GEMINI_MODELS:
        try:
            text = _generate(name, "Reply with the single word: ready", timeout_s=25)
            lines.append(f"{name}: OK ({text.strip()[:20]})")
            ok = True
        except Exception as exc:
            lines.append(_describe(name, exc))
    return ok, "\n".join(lines)