# UpNote

A lightweight Markdown editor built with Python. The desktop app uses PyQt6 and includes a live preview; the same editor is available as a browser preview on Streamlit Community Cloud.

[![Open live app](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://upnote.streamlit.app)

## Features

- Markdown editor with live HTML preview
- Syntax highlighting for headings, emphasis, code, highlights, subscript and superscript
- Light/dark theme
- Open and save `.md` files
- PNG background and icon assets preserved with alpha transparency in desktop builds
- Browser preview with upload and download support

## Requirements

Python 3.12+ is recommended for the Windows build.

## Run locally

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python upnote.py
```

To run the browser preview locally:

```powershell
streamlit run streamlit_app.py
```

## Windows release

Build a portable Windows executable and ZIP package:

```powershell
.\build_release.ps1 1.0.0
```

The output is created under `release\` as `UpNote-1.0.0-windows.zip`. The package is portable and includes the PNG assets; no Python installation is needed to run `UpNote.exe`.

## Streamlit Cloud deployment

1. Open [Streamlit Community Cloud](https://share.streamlit.io/).
2. Choose **Deploy an app**, select `lukaazman/UpNote`, branch `main`, and file `streamlit_app.py`.
3. Set the app name to `upnote` (or update the badge URL above if another name is chosen).
4. Every push to `main` redeploys the preview automatically.

The live preview is intended for quick browser testing of the Markdown editor. The full PyQt6 desktop experience remains available in the Windows release package.