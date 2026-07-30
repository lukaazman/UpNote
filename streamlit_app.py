"""UpNote browser preview for Streamlit Community Cloud."""

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
        --pink: #f745e0;
        --cyan: #45f1f7;
        --light: #ffffff;
        --dark: #2e2e2e;
      }}

      .stApp {{
        background: url("{asset_data_uri(BACKGROUND_PATH)}") no-repeat center center fixed;
        background-size: cover;
      }}

      [data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer {{
        visibility: hidden;
        height: 0;
      }}

      .block-container {{
        padding-top: 0.75rem;
        padding-bottom: 1rem;
      }}

      div[data-testid="stTextArea"] textarea {{
        background: url("{asset_data_uri(BACKGROUND_PATH)}") no-repeat center center !important;
        background-color: var(--light) !important;
        color: var(--pink) !important;
        font-size: 30px !important;
        font-family: Arial, sans-serif !important;
        line-height: 5.4 !important;
        border: none !important;
        padding: 40px !important;
      }}

      div[data-testid="stTextArea"] textarea:focus {{
        box-shadow: none !important;
        outline: none !important;
      }}

      .preview-shell {{
        font-family: Arial, sans-serif;
        line-height: 4.8;
        padding: 40px;
        max-width: 75%;
        margin: 40px auto;
        color: var(--pink);
        font-size: 30px;
        background-color: var(--light);
      }}

      .preview-shell pre {{
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 3px;
        overflow-x: auto;
      }}

      .preview-shell code {{
        font-family: Courier, monospace;
        background-color: #f0f0f0;
        padding: 5px 10px;
        border-radius: 3px;
      }}

      .preview-shell h1, .preview-shell h2, .preview-shell h3, .preview-shell h4, .preview-shell h5, .preview-shell h6 {{
        color: var(--cyan);
        font-weight: 800;
      }}

      .preview-shell a {{
        color: var(--cyan);
      }}

      .preview-shell blockquote {{
        border-left: 4px solid var(--cyan);
        margin-left: 0;
        padding-left: 1rem;
      }}

      @media (max-width: 900px) {{
        .preview-shell {{
          max-width: 100%;
          margin: 20px 0 0;
          padding: 24px;
          font-size: 24px;
          line-height: 1.7;
        }}

        div[data-testid="stTextArea"] textarea {{
          font-size: 24px !important;
          line-height: 1.7 !important;
          padding: 24px !important;
        }}
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

if "content" not in st.session_state:
    st.session_state.content = (
        "# Welcome to UpNote\n\n"
        "Write **Markdown** here and see the preview below.\n\n"
        "==Highlight==, `inline code`, and [links](https://github.com/lukaazman/UpNote) are supported.\n"
    )

st.session_state.content = st.text_area(
    "Markdown source",
    key="content",
    height=520,
    label_visibility="collapsed",
)

rendered = markdown.markdown(st.session_state.content)
st.markdown(f"<div class='preview-shell'>{rendered}</div>", unsafe_allow_html=True)
