"""Tab 2: Crack Diagnostics & Structural Integrity."""
import streamlit as st

from .. import styles, ui
from ..services import cracks as svc

STATE = "crack_result"


def render() -> None:
    st.subheader("Crack Diagnostics & Structural Integrity")
    st.caption("Upload a photo of a concrete or wall surface. Defects are classified with IS 456 width limits.")

    image = ui.pick_image("crack", "Surface photo (JPG or PNG)")
    left, right = st.columns([1, 1])
    with left:
        if image is not None:
            st.image(image, width="stretch")
    with right:
        if st.button("Diagnose defect", type="primary", disabled=image is None):
            ui.run_analysis(STATE, svc.PROMPT, image, svc.normalize, svc.demo_result)
        if image is None:
            st.caption("Upload a photo to enable the diagnosis.")

    result = st.session_state.get(STATE)
    if not result:
        return
    ui.mode_banner(result)
    data = result["data"]
    urgency = data["urgency"]

    cols = st.columns(3)
    cols[0].markdown(styles.metric("Defect type", data["defect_type"]), unsafe_allow_html=True)
    cols[1].markdown(styles.metric("Est. crack width", f"{data['estimated_width_mm']:.2f} mm"), unsafe_allow_html=True)
    cols[2].markdown(styles.metric("Urgency", urgency["level"], urgency["timeframe"]), unsafe_allow_html=True)

    check = data["is456_check"]
    styles.notice(f"<b>IS 456 width check:</b> {check['message']}", "ok" if check["within_limit"] else "bad")

    if data["summary"]:
        st.markdown(f'<div class="ciq-alert">{data["summary"]}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Root causes")
        for item in data["root_causes"]:
            st.markdown(f"- {item}")
    with c2:
        st.markdown("#### Recommended repairs")
        for item in data["recommended_repairs"]:
            st.markdown(f"- {item}")

    st.caption("A photo cannot confirm structural safety. High or Critical results need a physical inspection by a qualified engineer.")
    ui.json_download(data, "crack_diagnosis.json")
