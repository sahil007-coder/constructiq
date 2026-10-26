"""ConstructIQ: Multimodal Construction Intelligence Platform (entry point)."""
import streamlit as st

from constructiq import sidebar, styles
from constructiq.config import APP_NAME, APP_TAGLINE
from constructiq.tabs import assistant, cracks, planning, safety

st.set_page_config(page_title=f"{APP_NAME} | {APP_TAGLINE}", page_icon=styles.favicon(), layout="wide")
styles.inject()
sidebar.render()

st.markdown(
    f'<div class="ciq-hero"><h1>Construct<span>IQ</span></h1><p>{APP_TAGLINE}</p>'
    '<div class="tags"><span>OSHA 1926</span><span>IS 456</span><span>INR</span><span>GEMINI VISION</span></div></div>',
    unsafe_allow_html=True,
)

tab_safety, tab_cracks, tab_planning, tab_assistant = st.tabs(
    ["Site Safety & PPE", "Crack Diagnostics", "Planning & Valuation", "Daily Site Assistant"]
)
for tab, module in [(tab_safety, safety), (tab_cracks, cracks), (tab_planning, planning), (tab_assistant, assistant)]:
    with tab:
        try:
            module.render()
        except Exception as exc:  # keep one failing tab from taking down the app
            st.error(f"This section hit an error: {exc}")
