"""Sidebar: API key input, mode badge, architecture overview, navigation."""
import streamlit as st

from .config import APP_NAME, APP_TAGLINE, STANDARDS
from .gemini_client import KEY_STATE, is_live, test_connection

FEATURES = [
    ("01", "Site Safety & PPE Audit", "Photo-based PPE and hazard check"),
    ("02", "Crack Diagnostics", "Defect type, width, repair and urgency"),
    ("03", "Planning & Valuation", "Budget, materials and asset value in INR"),
    ("04", "Daily Site Assistant", "Weather alerts and engineering chat"),
]


def render() -> None:
    """Draw the sidebar."""
    with st.sidebar:
        st.markdown(f"### {APP_NAME}")
        st.caption(APP_TAGLINE)

        st.text_input(
            "Google Gemini API key",
            type="password",
            key=KEY_STATE,
            placeholder="Paste key (optional)",
            help="Kept only in this browser session. Leave empty to use demonstration mode.",
        )
        if is_live():
            dot, title, sub = "#3DDC97", "Live mode", "Gemini analysis active"
        else:
            dot, title, sub = "#F2B705", "Demonstration mode", "Sample analysis, no key needed"
        st.markdown(f'<div class="mode-badge"><span class="dot" style="background:{dot}"></span>'
                    f'<div><b>{title}</b><small>{sub}</small></div></div>', unsafe_allow_html=True)

        if is_live() and st.button("Test connection", width="stretch"):
            with st.spinner("Contacting Gemini..."):
                ok, detail = test_connection()
            (st.success if ok else st.error)("Connected" if ok else "Connection failed")
            st.code(detail, language="text")

        st.markdown("---")
        st.markdown("**Feature navigation**")
        for no, name, desc in FEATURES:
            st.markdown(f'<div class="nav-item"><span class="no">{no}</span><div>'
                        f'<div class="name">{name}</div><div class="desc">{desc}</div></div></div>',
                        unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("Architecture overview"):
            st.markdown(
                "- **Streamlit UI**: one page per module\n"
                "- **Gemini vision/chat**: structured JSON analysis\n"
                "- **Rule engine**: deterministic fallback when offline\n"
                "- **No database**: all state lives in the session"
            )
        with st.expander("Standards referenced"):
            for code, scope in STANDARDS.items():
                st.markdown(f"**{code}**: {scope}")