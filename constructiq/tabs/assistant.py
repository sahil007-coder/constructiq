"""Tab 4: Daily Site Assistant, weather advisory and chatbot."""
import streamlit as st

from .. import styles
from ..gemini_client import GeminiUnavailable, generate_chat, is_live
from ..services import chat as chat_svc
from ..services import weather as wx

HISTORY = "chat_history"


def _weather_section() -> str:
    st.subheader("Daily Site Assistant")
    st.markdown("#### Weather-aware advisory")
    condition = st.radio("Today's site weather", wx.CONDITIONS, horizontal=True, key="weather_condition")
    adv = wx.advisory_for(condition)
    st.markdown(f'<div class="ciq-alert">{styles.pill(adv["level"])} &nbsp;<b>{adv["headline"]}</b></div>',
                unsafe_allow_html=True)
    for alert in adv["alerts"]:
        with st.container(border=True):
            st.markdown(f'{styles.pill(alert["severity"])} &nbsp;**{alert["title"]}**', unsafe_allow_html=True)
            for action in alert["actions"]:
                st.markdown(f"- {action}")
            st.caption(f"Reference: {alert['standard']}")
    st.caption(chat_svc.DISCLAIMER)
    return condition


def _chat_section(condition: str) -> None:
    st.markdown("---")
    st.markdown("#### Construction engineering assistant")
    history = st.session_state.setdefault(HISTORY, [])

    cols = st.columns(len(chat_svc.SUGGESTIONS))
    picked = None
    for col, q in zip(cols, chat_svc.SUGGESTIONS):
        if col.button(q, key=f"sugg_{q}", width="stretch"):
            picked = q

    for turn in history:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])

    typed = st.chat_input("Ask about concrete, formwork, safety, codes...")
    question = typed or picked
    if question:
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = _answer(question, history, condition)
            st.markdown(answer)
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

    if history and st.button("Clear conversation"):
        st.session_state[HISTORY] = []
        st.rerun()


def _answer(question: str, history: list, condition: str) -> str:
    if is_live():
        try:
            return generate_chat(chat_svc.SYSTEM_PROMPT.format(weather=condition), history, question)
        except GeminiUnavailable:
            return chat_svc.offline_answer(question) + "\n\n*(Gemini was unavailable, so this came from the built-in notes.)*"
    return chat_svc.offline_answer(question)


def render() -> None:
    condition = _weather_section()
    _chat_section(condition)
