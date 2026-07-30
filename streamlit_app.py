"""Branded UpNote preview for Streamlit Community Cloud."""

from __future__ import annotations

from base64 import b64encode
from pathlib import Path

import markdown
import streamlit as st

ROOT = Path(__file__).resolve().parent
ICON_PATH = ROOT / "icon.png"
BACKGROUND_PATH = ROOT / "background.png"


def asset_data_uri(path: Path) -> str:
    return f"data:image/png;base64,{b64encode(path.read_bytes()).decode('ascii')}"


st.set_page_config(
    page_title="UpNote",
    page_icon=str(ICON_PATH),
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    f"""
    <style>
      :root {{
        --bg: #fff8fb;
        --panel: rgba(255, 255, 255, 0.84);
        --panel-strong: rgba(255, 255, 255, 0.94);
        --text: #221826;
        --muted: #6f6474;
        --accent: #f745e0;
        --accent-2: #6f5cff;
        --accent-3: #ff8cc8;
        --border: rgba(34, 24, 38, 0.10);
        --shadow: 0 26px 80px rgba(72, 22, 57, 0.16);
      }}

      .stApp {{
        background:
          radial-gradient(circle at top left, rgba(247, 69, 224, 0.18), transparent 28%),
          radial-gradient(circle at top right, rgba(111, 92, 255, 0.14), transparent 22%),
          linear-gradient(180deg, rgba(255, 248, 251, 0.94), rgba(255, 248, 251, 0.84)),
          url("{asset_data_uri(BACKGROUND_PATH)}");
        background-size: cover;
        background-attachment: fixed;
        color: var(--text);
      }}

      [data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer {{
        visibility: hidden;
        height: 0;
      }}

      .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
      }}

      .hero {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
        padding: 1rem 1.25rem;
        border: 1px solid var(--border);
        border-radius: 1.5rem;
        background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(255,255,255,0.72));
        box-shadow: var(--shadow);
        backdrop-filter: blur(18px);
      }}

      .brand-mark {{
        width: 3rem;
        height: 3rem;
        border-radius: 0.9rem;
        overflow: hidden;
        flex: 0 0 auto;
        box-shadow: 0 10px 28px rgba(247, 69, 224, 0.22);
      }}

      .brand-mark img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
      }}

      .eyebrow {{
        margin: 0;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: var(--accent);
        font-weight: 700;
      }}

      .title {{
        margin: 0.12rem 0 0;
        font-size: clamp(2rem, 4vw, 3.2rem);
        line-height: 1.02;
        font-weight: 800;
        color: var(--text);
      }}

      .subtitle {{
        margin: 0.35rem 0 0;
        color: var(--muted);
        font-size: 0.98rem;
      }}

      .pill-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.85rem;
      }}

      .pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.4rem 0.7rem;
        border-radius: 999px;
        font-size: 0.82rem;
        color: var(--text);
        background: rgba(255, 255, 255, 0.76);
        border: 1px solid var(--border);
      }}

      .panel {{
        padding: 1rem;
        border-radius: 1.4rem;
        border: 1px solid var(--border);
        background: var(--panel);
        box-shadow: var(--shadow);
        backdrop-filter: blur(18px);
      }}

      .panel--strong {{
        background: var(--panel-strong);
      }}

      .panel-title {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.75rem;
      }}

      .panel-title h3 {{
        margin: 0;
        font-size: 1rem;
      }}

      .meta {{
        color: var(--muted);
        font-size: 0.85rem;
      }}

      .card-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.8rem;
        margin-top: 0.8rem;
      }}

      .note-card {{
        padding: 0.9rem;
        border-radius: 1rem;
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(34,24,38,0.08);
      }}

      .note-card strong {{
        display: block;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
      }}

      .note-card span {{
        color: var(--muted);
        font-size: 0.82rem;
      }}

      div[data-testid="stTextArea"] textarea {{
        border-radius: 1rem !important;
        border: 1px solid rgba(34, 24, 38, 0.14) !important;
        background: rgba(255, 255, 255, 0.94) !important;
        color: var(--text) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.5);
      }}

      div[data-testid="stFileUploader"] section {{
        border-radius: 1rem;
        border: 1px dashed rgba(247, 69, 224, 0.28);
        background: rgba(255, 255, 255, 0.78);
      }}

      div[data-testid="stDownloadButton"] button,
      div[data-testid="stButton"] button {{
        border-radius: 999px !important;
        border: 0 !important;
        background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 0.65rem 1rem !important;
        box-shadow: 0 18px 30px rgba(111, 92, 255, 0.22) !important;
      }}

      .preview-shell {{
        padding: 1rem 1rem 1.1rem;
        border-radius: 1.3rem;
        background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(255,255,255,0.84));
        border: 1px solid rgba(34,24,38,0.08);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.8);
      }}

      .preview-content {{
        color: var(--text);
        line-height: 1.65;
      }}

      .preview-content h1, .preview-content h2, .preview-content h3 {{
        margin-top: 1.2em;
        margin-bottom: 0.45em;
      }}

      .preview-content code {{
        background: rgba(111, 92, 255, 0.09);
        padding: 0.14rem 0.35rem;
        border-radius: 0.45rem;
      }}

      .preview-content blockquote {{
        border-left: 4px solid var(--accent);
        margin-left: 0;
        padding-left: 1rem;
        color: var(--muted);
      }}

      .preview-content a {{
        color: var(--accent-2);
      }}

      .footer-note {{
        margin-top: 0.85rem;
        color: var(--muted);
        font-size: 0.82rem;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

if "content" not in st.session_state:
    st.session_state.content = (
        "# Welcome to UpNote\n\n"
        "Write **Markdown** on the left and see the polished preview on the right.\n\n"
        "- Fast drafting\n"
        "- Clean formatting\n"
        "- Shared from Streamlit Cloud\n\n"
        "> This preview is branded to match the app instead of the default Streamlit template.\n"
    )

uploaded = st.file_uploader("Open a Markdown file", type=["md", "markdown"])
if uploaded is not None:
    st.session_state.content = uploaded.getvalue().decode("utf-8")

content = st.session_state.content
word_count = len(content.split())
line_count = content.count("\n") + 1
char_count = len(content)

st.markdown(
    f"""
    <div class="hero">
      <div class="brand-mark"><img src="{asset_data_uri(ICON_PATH)}" alt="UpNote icon"></div>
      <div>
        <p class="eyebrow">UpNote preview</p>
        <h1 class="title">Your note app, not the default Streamlit template.</h1>
        <p class="subtitle">A branded browser preview that keeps the icon, palette, spacing, and editor flow aligned with UpNote.</p>
        <div class="pill-row">
          <span class="pill">{word_count} words</span>
          <span class="pill">{line_count} lines</span>
          <span class="pill">{char_count} chars</span>
          <span class="pill">Community Cloud friendly</span>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.05, 1.0], gap="large")

with left:
    st.markdown(
        """
        <div class="panel panel--strong">
          <div class="panel-title">
            <h3>Editor</h3>
            <span class="meta">Markdown source</span>
          </div>
        """,
        unsafe_allow_html=True,
    )
    content = st.text_area(
        "Markdown source",
        key="content",
        height=520,
        label_visibility="collapsed",
    )
    save_col, hint_col = st.columns([0.42, 0.58])
    with save_col:
        st.download_button(
            "Save Markdown",
            data=content,
            file_name="upnote.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with hint_col:
        st.markdown(
            "<div class='footer-note'>Drag in a `.md` file, edit inline, then export the exact text you wrote.</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    rendered = markdown.markdown(content, extensions=["extra", "sane_lists", "smarty"])
    st.markdown(
        """
        <div class="panel">
          <div class="panel-title">
            <h3>Preview</h3>
            <span class="meta">Rendered output</span>
          </div>
          <div class="preview-shell">
            <div class="preview-content">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(rendered, unsafe_allow_html=True)
    st.markdown(
        """
            </div>
          </div>
        </div>
        <div class="card-grid">
          <div class="note-card"><strong>Focused</strong><span>Minimal chrome and a calm reading surface.</span></div>
          <div class="note-card"><strong>Branded</strong><span>Icon, palette, and layout stay on theme.</span></div>
          <div class="note-card"><strong>Portable</strong><span>Works as a plain Streamlit Community Cloud app.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
