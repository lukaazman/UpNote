"""Browser preview for UpNote, suitable for Streamlit Community Cloud."""

import markdown
import streamlit as st

st.set_page_config(page_title="UpNote preview", page_icon="📝", layout="wide")
st.title("UpNote")
st.caption("Markdown editor preview — changes render instantly in the browser.")

default_text = """# Welcome to UpNote

Write **Markdown** on the left and see the rendered preview on the right.

==Highlight==, `inline code`, and [links](https://github.com/lukaazman/UpNote) are supported.
"""

if "content" not in st.session_state:
    st.session_state.content = default_text

uploaded = st.file_uploader("Open a Markdown file", type=["md", "markdown"])
if uploaded is not None:
    st.session_state.content = uploaded.getvalue().decode("utf-8")

left, right = st.columns(2)
with left:
    st.subheader("Editor")
    content = st.text_area("Markdown source", key="content", height=520, label_visibility="collapsed")
    st.download_button("Save Markdown", data=content, file_name="upnote.md", mime="text/markdown")

with right:
    st.subheader("Preview")
    st.markdown(markdown.markdown(content, extensions=["extra", "sane_lists"]), unsafe_allow_html=True)