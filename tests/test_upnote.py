import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtCore import QPoint, QSettings  # noqa: E402
from PyQt6.QtGui import QColor, QImage, QPainter, QTextFormat  # noqa: E402
from PyQt6.QtWidgets import QApplication, QMessageBox  # noqa: E402

import upnote  # noqa: E402

_settings_dir = tempfile.TemporaryDirectory()  # keep test settings out of the registry
QSettings.setDefaultFormat(QSettings.Format.IniFormat)
QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, _settings_dir.name)

app = QApplication.instance() or QApplication(sys.argv)
app.setOrganizationName("UpNoteTest")
app.setApplicationName("UpNoteTest")


def make_window(theme="light"):
    QSettings().clear()
    if theme:
        QSettings().setValue("theme", theme)
    with mock.patch.object(upnote, "system_animations_enabled", return_value=False):
        window = upnote.MarkdownEditor()
    window.resize(1200, 800)
    window.show()
    app.processEvents()
    return window


class HighlighterTests(unittest.TestCase):
    def setUp(self):
        self.window = make_window()
        self.doc = self.window.editor.document()

    def tearDown(self):
        self.doc.setModified(False)
        self.window.close()

    def formats_of(self, line_no):
        return self.doc.findBlockByNumber(line_no).layout().formats()

    def test_fenced_block_is_code_until_closing_fence(self):
        self.window.editor.setPlainText("before\n```\nprint(1)\n```\nafter")
        state = [self.doc.findBlockByNumber(i).userState() for i in range(5)]
        self.assertEqual(state, [0, 1, 1, 0, 0])
        inner = self.formats_of(2)
        self.assertTrue(inner and upnote.CODE_FONT in inner[0].format.fontFamilies())
        self.assertEqual(self.formats_of(4), [])

    def test_shift_enter_after_heading_starts_plain_line(self):
        from PyQt6.QtCore import Qt
        from PyQt6.QtTest import QTest
        editor = self.window.editor
        editor.setPlainText("# naslov")
        editor.moveCursor(editor.textCursor().MoveOperation.End)
        for mods in (Qt.KeyboardModifier.ShiftModifier, Qt.KeyboardModifier.ControlModifier):
            QTest.keyClick(editor, Qt.Key.Key_Return, mods)
        QTest.keyClicks(editor, "naslov")
        self.assertEqual(self.doc.blockCount(), 3)
        self.assertNotIn(" ", editor.document().toRawText())
        self.assertEqual(self.formats_of(2), [])

    def test_single_backtick_still_works(self):
        self.window.editor.setPlainText("a `x` b")
        families = [r.format.fontFamilies() for r in self.formats_of(0)]
        self.assertTrue(any(f and upnote.CODE_FONT in f for f in families))

    def test_heading_pixel_size_scales_with_zoom(self):
        self.window.editor.setPlainText("# Title")
        size = lambda: self.formats_of(0)[-1].format.property(QTextFormat.Property.FontPixelSize)
        self.assertEqual(size(), round(upnote.BASE_TEXT_PX * 2))
        self.window.set_zoom(200)
        self.assertEqual(size(), round(upnote.BASE_TEXT_PX * 2 * 2))


class ZoomTests(unittest.TestCase):
    def test_clamp_and_reset(self):
        window = make_window()
        for _ in range(40):
            window.step_zoom(1)
        self.assertEqual(window.zoom, upnote.ZOOM_MAX)
        for _ in range(40):
            window.step_zoom(-1)
        self.assertEqual(window.zoom, upnote.ZOOM_MIN)
        window.step_zoom(0)
        self.assertEqual(window.zoom, 100)
        self.assertIn(f"font-size: {round(upnote.BASE_MENU_PX)}px", window.styleSheet())
        window.close()


class InvertTests(unittest.TestCase):
    def test_text_over_glyph_takes_theme_colour(self):
        window = make_window()
        bg = window.background
        rect = bg.mark_rect()
        # Probe a point inside the arrow stem (left glyph), and one in the gap between glyphs.
        stem = QPoint(int(rect.left() + rect.width() * 0.205), int(rect.top() + rect.height() * 0.75))
        gap = QPoint(int(rect.left() + rect.width() * 0.43), int(rect.top() + rect.height() * 0.5))
        glyphs = QImage(bg.size(), QImage.Format.Format_ARGB32_Premultiplied)
        glyphs.fill(0)
        p = QPainter(glyphs)
        bg.draw_glyphs(p)
        p.end()
        self.assertGreater(glyphs.pixelColor(stem).alpha(), 240)
        self.assertEqual(glyphs.pixelColor(gap).alpha(), 0)

        window.editor.setPlainText("\n".join(["█" * 400] * 80))
        app.processEvents()
        shot = window.background.grab().toImage()
        light = QColor(upnote.THEMES["light"]["bg"])
        text = QColor(upnote.THEMES["light"]["text"])
        # Scan the stem and gap columns: solid text lines cross both, so inside the
        # glyph we must find theme-coloured text and in the gap normal text colour.
        # Most of the stem must be theme-coloured (the rest is pink glyph in line gaps).
        def column(x):
            ys = range(int(rect.top()), int(rect.bottom()))
            return [(glyphs.pixelColor(x, y).alpha(), shot.pixelColor(x, y).rgb()) for y in ys]
        stem_px = column(stem.x())
        gap_px = column(gap.x())
        self.assertTrue(any(a == 255 and rgb == light.rgb() for a, rgb in stem_px))
        self.assertTrue(any(a == 0 and rgb == text.rgb() for a, rgb in gap_px))
        solid = [rgb for a, rgb in stem_px if a == 255]
        self.assertGreater(solid.count(light.rgb()) / len(solid), 0.6)
        window.editor.document().setModified(False)
        window.close()


class ThemeTests(unittest.TestCase):
    def test_only_light_and_dark_default_follows_system(self):
        window = make_window(theme=None)
        self.assertEqual(sorted(window.theme_actions), ["dark", "light"])
        expected = window.resolved_theme()
        self.assertIn(expected, ("light", "dark"))
        self.assertTrue(window.theme_actions[expected].isChecked())
        window.set_theme_mode("dark")
        self.assertTrue(window.theme_actions["dark"].isChecked())
        self.assertEqual(QSettings().value("theme"), "dark")
        window.close()


class LayoutTests(unittest.TestCase):
    def test_side_margin_matches_original_spacers(self):
        window = make_window()
        margins = window.editor.viewportMargins()
        width = window.editor.width()
        self.assertEqual(margins.left(), int(width * upnote.SIDE_FRACTION) + upnote.SIDE_PAD)
        self.assertEqual(margins.left(), margins.right())
        window.close()


class FileTests(unittest.TestCase):
    def test_bad_encoding_warns_instead_of_crashing(self):
        window = make_window()
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp, "bad.md")
            bad.write_bytes(b"\xff\xfe\xfa not utf8")
            with mock.patch.object(QMessageBox, "warning") as warning:
                self.assertFalse(window.load_path(bad))
            warning.assert_called_once()

    def test_save_roundtrip_and_title(self):
        window = make_window()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "note.md")
            window.editor.insertPlainText("hello")
            self.assertIn("•", window.windowTitle())
            self.assertTrue(window._write(path))
            self.assertEqual(path.read_text(encoding="utf-8"), "hello")
            self.assertEqual(window.windowTitle(), "note.md — UpNote")
            self.assertTrue(window.load_path(path))
            self.assertFalse(window.editor.document().isModified())
        window.close()


if __name__ == "__main__":
    unittest.main()
