"""Light blueprint theme and small HTML helpers (cards, pills, notices)."""
import streamlit as st
from PIL import Image, ImageDraw

CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

  :root {
    --paper: #F4F1E8; --card: #FFFFFF; --ink: #12285A; --ink-2: #51607F;
    --line: #C5D0E4; --accent: #F2B705; --accent-ink: #5C4600;
    --ok: #1E8E5A; --low: #2F6FD0; --med: #A87900; --high: #C85F12; --crit: #C62F3D;
  }
  html, body, .stApp, .stApp *:not([data-testid="stIconMaterial"]) {
    font-family: 'IBM Plex Sans', system-ui, sans-serif; }
  .ciq-pill, .ciq-metric .label, .nav-item .no, .ciq-hero .tags span {
    font-family: 'IBM Plex Mono', ui-monospace, monospace !important; }
  .stApp { background: var(--paper); color: var(--ink); }
  h1, h2, h3, h4, h5 { font-family: 'IBM Plex Sans', system-ui, sans-serif; font-weight: 700;
                       letter-spacing: -0.01em; color: var(--ink); }
  h4 { margin-top: 1.5rem; }
  header[data-testid="stHeader"] { background: transparent; }
  .block-container { padding-top: 2rem; max-width: 1180px; }

  /* ---- hero: blueprint grid with hazard-stripe edge ---- */
  .ciq-hero { position: relative; padding: 1.6rem 1.8rem 1.9rem; margin-bottom: 1.4rem;
              border-radius: 6px; color: #fff; overflow: hidden;
              background:
                repeating-linear-gradient(0deg, rgba(255,255,255,.08) 0 1px, transparent 1px 26px),
                repeating-linear-gradient(90deg, rgba(255,255,255,.08) 0 1px, transparent 1px 26px),
                var(--ink); }
  .ciq-hero::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 8px;
                     background: repeating-linear-gradient(-45deg, var(--accent) 0 12px, var(--ink) 12px 24px); }
  .ciq-hero h1 { font-size: 2.3rem; margin: 0; color: #fff; }
  .ciq-hero h1 span { color: var(--accent); }
  .ciq-hero p { margin: 0.35rem 0 0; color: #C9D6F2; font-size: 0.95rem; }
  .ciq-hero .tags { margin-top: 0.8rem; display: flex; gap: 0.5rem; flex-wrap: wrap; }
  .ciq-hero .tags span { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; font-weight: 600;
                         padding: 2px 9px; border: 1px solid rgba(255,255,255,.35); border-radius: 3px;
                         letter-spacing: .05em; color: #fff; }

  /* ---- tabs as solid segments ---- */
  [role="tablist"] { gap: 0.35rem; border-bottom: 2px solid var(--ink); }
  .react-aria-SelectionIndicator { display: none !important; }
  [data-testid="stTab"] { padding: 0.55rem 1rem; border-radius: 5px 5px 0 0; background: transparent; }
  [data-testid="stTab"] p { font-weight: 600; color: var(--ink-2); margin: 0; }
  [data-testid="stTab"][aria-selected="true"] { background: var(--ink); }
  [data-testid="stTab"][aria-selected="true"] p { color: #fff; }
  [data-testid="stTab"]:hover p { color: var(--ink); }
  [data-testid="stTab"][aria-selected="true"]:hover p { color: #fff; }

  /* ---- cards and metrics ---- */
  .ciq-card { background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--ink);
              border-radius: 4px; padding: 0.9rem 1.2rem; margin-bottom: 0.8rem; }
  .ciq-metric { background: var(--card); border: 1px solid var(--line); border-top: 4px solid var(--accent);
                border-radius: 4px; padding: 0.85rem 1.1rem; margin-bottom: 0.8rem;
                box-shadow: 3px 3px 0 rgba(18,40,90,.07); }
  .ciq-metric .label { font-family: 'IBM Plex Mono', monospace; color: var(--ink-2); font-size: 0.7rem;
                       text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; }
  .ciq-metric .value { font-size: 1.45rem; font-weight: 700; margin-top: 0.2rem; color: var(--ink); }
  .ciq-metric .sub { color: var(--ink-2); font-size: 0.8rem; margin-top: 0.1rem; }

  /* ---- badges ---- */
  .ciq-pill { display: inline-block; padding: 1px 9px; border-radius: 3px; font-size: 0.72rem;
              font-family: 'IBM Plex Mono', monospace; font-weight: 600; letter-spacing: .04em;
              text-transform: uppercase; border: 1px solid; vertical-align: middle; }
  .pill-ok       { color: var(--ok);   border-color: var(--ok);   background: #E6F5EE; }
  .pill-low      { color: var(--low);  border-color: var(--low);  background: #E8F0FC; }
  .pill-medium   { color: var(--med);  border-color: var(--med);  background: #FBF3D9; }
  .pill-high     { color: var(--high); border-color: var(--high); background: #FCEBDD; }
  .pill-critical { color: var(--crit); border-color: var(--crit); background: #FBE5E7; }
  .pill-neutral  { color: var(--ink-2); border-color: var(--line); background: #EEF1F7; }

  /* ---- notices and alerts ---- */
  .ciq-notice { border: 1px solid var(--line); border-left: 4px solid var(--low); background: #fff;
                border-radius: 4px; padding: 0.65rem 1rem; margin: 0.6rem 0; font-size: 0.92rem; }
  .ciq-notice.warn { border-left-color: var(--high); background: #FFF8F0; }
  .ciq-notice.ok   { border-left-color: var(--ok); background: #F3FBF7; }
  .ciq-notice.bad  { border-left-color: var(--crit); background: #FEF4F5; }
  .ciq-alert { border-left: 4px solid var(--accent); background: #fff; border: 1px solid var(--line);
               border-left: 4px solid var(--accent); padding: 0.7rem 1rem; border-radius: 4px; margin: 0.6rem 0; }

  /* ---- controls ---- */
  .stButton > button, .stDownloadButton > button { border-radius: 4px; font-weight: 600;
                                                   border: 1.5px solid var(--ink); }
  .stButton > button[kind="primary"] { background: var(--ink); color: #fff; }
  .stButton > button[kind="primary"]:hover { background: #1D3A7A; border-color: #1D3A7A; color: #fff; }
  .stButton > button[kind="secondary"], .stDownloadButton > button { background: #fff; color: var(--ink); }
  .stButton > button[kind="secondary"]:hover, .stDownloadButton > button:hover { background: var(--accent); border-color: var(--ink); color: var(--ink); }
  div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 4px; }

  /* ---- sidebar ---- */
  section[data-testid="stSidebar"] { border-right: 4px solid var(--accent); }
  section[data-testid="stSidebar"] h3 { color: #fff; }
  .nav-item { display: flex; gap: 0.7rem; padding: 0.45rem 0; border-bottom: 1px solid rgba(255,255,255,.12); }
  .nav-item .no { font-family: 'IBM Plex Mono', monospace; color: var(--accent); font-weight: 600; font-size: 0.8rem; padding-top: 2px; }
  .nav-item .name { color: #fff; font-weight: 600; font-size: 0.92rem; }
  .nav-item .desc { color: #B9C8E8; font-size: 0.78rem; }
  .mode-badge { display: flex; align-items: center; gap: 0.55rem; padding: 0.55rem 0.8rem; border-radius: 4px;
                background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.2); margin: 0.4rem 0 0.2rem;
                font-size: 0.85rem; color: #fff; }
  .mode-badge .dot { width: 9px; height: 9px; border-radius: 50%; flex: none; }
  .mode-badge small { color: #B9C8E8; display: block; font-size: 0.75rem; }
</style>
"""

NOTICE_KINDS = {"info", "warn", "ok", "bad"}


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def favicon() -> Image.Image:
    """Small drawn logo mark: a building outline on blueprint blue."""
    size = 128
    img = Image.new("RGB", (size, size), "#12285A")
    d = ImageDraw.Draw(img)
    d.rectangle([28, 40, 76, 104], fill="#F2B705")          # tower
    d.rectangle([76, 64, 100, 104], fill="#F4F1E8")         # annex
    for y in (52, 68, 84):                                  # windows
        d.rectangle([38, y, 48, y + 7], fill="#12285A")
        d.rectangle([56, y, 66, y + 7], fill="#12285A")
    d.line([(20, 108), (108, 108)], fill="#F2B705", width=5)  # ground line
    return img


def pill(text: str, level: str | None = None) -> str:
    cls = (level or text).lower()
    if cls not in {"ok", "low", "medium", "high", "critical", "neutral"}:
        cls = "neutral"
    return f'<span class="ciq-pill pill-{cls}">{text}</span>'


def notice(text: str, kind: str = "info") -> None:
    kind = kind if kind in NOTICE_KINDS else "info"
    cls = "" if kind == "info" else f" {kind}"
    st.markdown(f'<div class="ciq-notice{cls}">{text}</div>', unsafe_allow_html=True)


def metric(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    return (f'<div class="ciq-metric"><div class="label">{label}</div>'
            f'<div class="value">{value}</div>{sub_html}</div>')
