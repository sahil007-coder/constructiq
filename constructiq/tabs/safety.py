"""Tab 1: Site Safety & PPE Audit."""
import streamlit as st

from .. import styles, ui
from ..services import safety as svc

STATE = "safety_result"
LABELS = {"worn": "Worn", "missing": "Missing", "not_visible": "Not visible", "not_applicable": "N/A"}
LEVELS = {"worn": "ok", "missing": "critical", "not_visible": "neutral", "not_applicable": "neutral"}


def render() -> None:
    st.subheader("Site Safety & PPE Audit")
    st.caption("Upload a site photo. Checks PPE and hazards against OSHA 29 CFR 1926 and IS 456.")

    image = ui.pick_image("safety", "Site photo (JPG or PNG)")
    left, right = st.columns([1, 1])
    with left:
        if image is not None:
            st.image(image, width="stretch")
    with right:
        if st.button("Run safety audit", type="primary", disabled=image is None):
            ui.run_analysis(STATE, svc.PROMPT, image, svc.normalize, svc.demo_result)
        if image is None:
            st.caption("Upload a photo to enable the audit.")

    result = st.session_state.get(STATE)
    if not result:
        return
    ui.mode_banner(result)
    data = result["data"]

    cols = st.columns(4)
    tiles = [("Safety score", f"{data['safety_score']}/100", ""),
             ("Overall status", data["overall_status"], ""),
             ("Workers seen", str(data["workers_detected"]), ""),
             ("Hazards", str(len(data["hazards"])), "identified")]
    for col, (label, value, sub) in zip(cols, tiles):
        col.markdown(styles.metric(label, value, sub), unsafe_allow_html=True)
    st.progress(data["safety_score"] / 100)

    if data["summary"]:
        st.markdown(f'<div class="ciq-alert">{data["summary"]}</div>', unsafe_allow_html=True)

    st.markdown("#### PPE checklist")
    ppe_cols = st.columns(len(svc.PPE_ITEMS))
    for col, (key, name) in zip(ppe_cols, svc.PPE_ITEMS.items()):
        item = data["ppe_detection"][key]
        col.markdown(f"**{name}**<br>{styles.pill(LABELS[item['status']], LEVELS[item['status']])}",
                     unsafe_allow_html=True)
        if item["note"]:
            col.caption(item["note"])

    st.markdown("#### Identified hazards")
    if not data["hazards"]:
        styles.notice("No hazards identified in this photo.", "ok")
    for h in data["hazards"]:
        st.markdown(
            f'<div class="ciq-card">{styles.pill(h["severity"])} &nbsp;<b>{h["description"]}</b><br>'
            f'<small>Standard: {h["standard"] or "n/a"}</small><br>'
            f'<b>Remedy:</b> {h["remedy"] or "n/a"}</div>',
            unsafe_allow_html=True,
        )

    ui.json_download(data, "safety_audit.json")
