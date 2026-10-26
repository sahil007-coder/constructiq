"""Whole-app smoke tests using Streamlit's AppTest runner (demo mode, no network)."""
import io
from pathlib import Path

from PIL import Image
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "app.py"


def _app():
    return AppTest.from_file(str(APP), default_timeout=30).run()


def _png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), (120, 120, 120)).save(buf, format="PNG")
    return buf.getvalue()


def test_app_loads_with_four_tabs_and_demo_mode():
    at = _app()
    assert not at.exception
    assert len(at.tabs) == 4
    assert any("Demonstration mode" in m.value for m in at.sidebar.markdown)
    assert [w.label for w in at.sidebar.text_input] == ["Google Gemini API key"]


def test_weather_conditions_all_render():
    at = _app()
    radio = [r for r in at.radio if r.key == "weather_condition"][0]
    for cond in ["High Wind", "Heavy Rain", "Extreme Heat", "Normal"]:
        radio.set_value(cond).run()
        assert not at.exception


def test_chat_answers_offline():
    at = _app()
    at.chat_input[0].set_value("How long should concrete be cured?").run()
    assert not at.exception
    assert any("7 days" in m.markdown[0].value for m in at.chat_message)


def test_safety_and_crack_flows_in_demo_mode():
    at = _app()
    # file_uploader values are set through the AppTest element API
    for uploader_key, button, state in [("safety_upload", "Run safety audit", "safety_result"),
                                        ("crack_upload", "Diagnose defect", "crack_result")]:
        uploader = [u for u in at.file_uploader if u.key == uploader_key][0]
        uploader.upload("site.png", _png_bytes(), "image/png").run()
        [b for b in at.button if b.label == button][0].click().run()
        assert not at.exception
        assert at.session_state[state]["mode"] == "demo"
