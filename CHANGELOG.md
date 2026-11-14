# Changelog

## UpNote 1.1.0

- Redesigned logo and background: the arrow and N are redrawn as clean vector
  shapes with motion streaks, on a plain white icon. The background glyphs fly in
  once at startup (skipped when Windows animations are off).
- Editor text switches to the theme colour exactly where it crosses the logo glyphs.
- New typography: Segoe UI Variable for text and menus; code stays Consolas.
- Keyboard zoom for text and menu bar: Ctrl + / -, Ctrl+0, Ctrl + mouse wheel.
- Theme menu with Light and Dark (default follows Windows); switching crossfades.
- Dimmed Markdown markers.
- Title shows unsaved changes; closing, opening or creating a file asks before discarding edits.
- Remembers theme, zoom, window size and last file. Opens files by drag and drop or command line.
- Fixed: ``` fenced code blocks were not highlighted.
- Fixed: pasting from a web page kept its fonts and colours.
- Fixed: opening a non-UTF-8 file or a failed save crashed the app.
- Fixed: heading sizes were set in points against a pixel base.
- Fixed: Shift+Enter after a heading kept the next line styled as a heading.
- Removed the hidden HTML preview (Chromium/QtWebEngine and Markdown dependencies).
  The Windows build shrinks from over 200 MB to about 23 MB.
- Repository tidied into `assets/`, `scripts/` and `tests/`.

## UpNote 1.0.2

- Fixed light-theme crash when switching themes.
- The PNG background is now rendered once, centered, behind the editor.
- Unified dark-mode window, editor, and menu background color for a seamless appearance.
