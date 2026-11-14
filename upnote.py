import sys
from pathlib import Path

from PyQt6.QtCore import (
    QEasingCurve, QPoint, QPointF, QPropertyAnimation, QRectF, QRegularExpression,
    QSettings, Qt, QTimer, QVariantAnimation, pyqtSignal,
)
from PyQt6.QtGui import (
    QAction, QActionGroup, QColor, QFont, QGuiApplication, QIcon, QKeySequence, QPainter,
    QPixmap, QShortcut, QSyntaxHighlighter, QTextBlockFormat, QTextCharFormat,
    QTextCursor, QTextFormat,
)
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QGraphicsEffect, QGraphicsOpacityEffect, QLabel,
    QMainWindow, QMessageBox, QTextEdit, QVBoxLayout, QWidget,
)

BODY_FONT = "Segoe UI Variable Text"
MENU_FONT = "Segoe UI Variable Display"
CODE_FONT = "Consolas"
BASE_TEXT_PX = 20
BASE_MENU_PX = 14
ZOOM_MIN, ZOOM_MAX, ZOOM_STEP = 50, 300, 10
SIDE_FRACTION = 0.125  # matches the original 12.5 % side spacers
SIDE_PAD = 40
FILE_FILTER = "Markdown Files (*.md *.markdown);;Text Files (*.txt);;All Files (*)"

THEMES = {
    "light": {
        "bg": "#ffffff", "text": "#f745e0", "accent": "#45f1f7",
        "menu_text": "#f745e0", "menu_sel_bg": "#f745e0", "menu_sel_text": "#ffffff",
        "selection": "#45f1f7",
    },
    "dark": {
        "bg": "#2e2e2e", "text": "#f745e0", "accent": "#45f1f7",
        "menu_text": "#45f1f7", "menu_sel_bg": "#45f1f7", "menu_sel_text": "#2e2e2e",
        "selection": "#f745e0",
    },
}


def resource_path(filename):
    """Return an asset path that works from source and from a PyInstaller build."""
    bundle_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return str(bundle_dir / filename)


def system_animations_enabled():
    """Honour Windows 'Show animations in Windows' (the OS reduced-motion switch)."""
    if sys.platform != "win32":
        return True
    import ctypes
    value = ctypes.c_int(1)
    ok = ctypes.windll.user32.SystemParametersInfoW(0x1042, 0, ctypes.byref(value), 0)
    return bool(value.value) if ok else True


def clamp_zoom(value):
    return max(ZOOM_MIN, min(ZOOM_MAX, value))


def with_alpha(color, alpha):
    c = QColor(color)
    c.setAlphaF(alpha)
    return c


def build_qss(c, text_px, menu_px):
    return f"""
        QTextEdit, QTextEdit QWidget {{ background: transparent; border: none; }}
        QTextEdit {{
            color: {c['text']};
            font-family: "{BODY_FONT}", "Segoe UI", sans-serif;
            font-size: {text_px}px;
            selection-background-color: {c['selection']};
            selection-color: {c['bg']};
        }}
        QMenuBar {{
            background: {c['bg']}; color: {c['menu_text']};
            font-family: "{MENU_FONT}", "Segoe UI", sans-serif; font-size: {menu_px}px;
            padding: {round(menu_px * 0.3)}px {round(menu_px * 0.6)}px;
        }}
        QMenuBar::item {{
            background: transparent; padding: {round(menu_px * 0.3)}px {round(menu_px * 0.75)}px;
            border-radius: {round(menu_px * 0.4)}px;
        }}
        QMenuBar::item:selected, QMenuBar::item:pressed {{
            background: {c['menu_sel_bg']}; color: {c['menu_sel_text']};
        }}
        QMenu {{
            background: {c['bg']}; color: {c['menu_text']}; border: none;
            font-family: "{MENU_FONT}", "Segoe UI", sans-serif; font-size: {menu_px}px;
            padding: {round(menu_px * 0.4)}px;
        }}
        QMenu::item {{
            padding: {round(menu_px * 0.4)}px {round(menu_px * 1.8)}px {round(menu_px * 0.4)}px {round(menu_px * 0.9)}px;
            border-radius: {round(menu_px * 0.4)}px;
        }}
        QMenu::item:selected {{ background: {c['menu_sel_bg']}; color: {c['menu_sel_text']}; }}
        QMenu::separator {{ height: {round(menu_px * 0.5)}px; }}
        QMessageBox {{ background: {c['bg']}; }}
        QMessageBox QLabel {{ color: {c['menu_text']}; font-family: "{BODY_FONT}", "Segoe UI"; }}
    """


class CenteredBackground(QWidget):
    """Paint the theme colour and the two logo layers (arrow, N) centred behind
    the editor. The layers fly in once at startup."""

    glyphs_moved = pyqtSignal()
    RISE = 40  # px travel of the startup motion

    def __init__(self):
        super().__init__()
        self._layers = [QPixmap(resource_path("assets/mark-arrow.png")),
                        QPixmap(resource_path("assets/mark-n.png"))]
        self._color = QColor("white")
        self._progress = 1.0
        self._anim = None

    def set_theme_color(self, color):
        self._color = QColor(color)
        self.update()

    def mark_rect(self):
        layer = self._layers[0]
        if layer.isNull():
            return QRectF()
        h = max(120.0, self.height() * 0.26)
        w = h * layer.width() / layer.height()
        return QRectF((self.width() - w) / 2, (self.height() - h) / 2, w, h)

    def draw_glyphs(self, painter):
        """Draw both layers in this widget's coordinates; also used as the text-invert mask."""
        rect = self.mark_rect()
        if rect.isNull():
            return
        t = self._progress
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setOpacity(t)
        offsets = [QPointF(0, (1 - t) * self.RISE), QPointF(-(1 - t) * self.RISE, 0)]
        for layer, offset in zip(self._layers, offsets):
            painter.drawPixmap(rect.translated(offset), layer, QRectF(layer.rect()))
        painter.restore()

    def animate_in(self):
        self._anim = QVariantAnimation(self, startValue=0.0, endValue=1.0, duration=600,
                                       easingCurve=QEasingCurve(QEasingCurve.Type.OutCubic))
        self._anim.valueChanged.connect(self._set_progress)
        self._anim.start()

    def _set_progress(self, value):
        self._progress = float(value)
        self.update()
        self.glyphs_moved.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.glyphs_moved.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._color)
        self.draw_glyphs(painter)


class GlyphInvertEffect(QGraphicsEffect):
    """Recolour editor text to the theme colour exactly where it overlaps the logo
    glyph pixels. The viewport is transparent, so its source pixmap is text only."""

    def __init__(self, background, viewport):
        super().__init__(viewport)
        self._background = background
        self._viewport = viewport
        self.color = QColor("white")

    def draw(self, painter):
        pixmap, offset = self.sourcePixmap(Qt.CoordinateSystem.LogicalCoordinates)
        if pixmap.isNull():
            return
        # Tint pixel (0,0) sits at viewport point `offset`; map that into background coords.
        origin = self._viewport.mapTo(self._background, QPoint(0, 0)) + offset
        # Full-size mask: composition modes only touch pixels a draw call covers.
        mask = QPixmap(pixmap.size())
        mask.setDevicePixelRatio(pixmap.devicePixelRatio())
        mask.fill(Qt.GlobalColor.transparent)
        p = QPainter(mask)
        p.translate(-origin.x(), -origin.y())
        self._background.draw_glyphs(p)
        p.end()
        painter.drawPixmap(offset, self._masked(pixmap, mask, QPainter.CompositionMode.CompositionMode_DestinationOut))
        painter.drawPixmap(offset, self._masked(pixmap, mask, QPainter.CompositionMode.CompositionMode_DestinationIn,
                                                self.color))

    @staticmethod
    def _masked(pixmap, mask, mode, fill=None):
        out = QPixmap(pixmap)
        p = QPainter(out)
        if fill is not None:
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            p.fillRect(QRectF(0, 0, out.width(), out.height()), fill)
        p.setCompositionMode(mode)
        p.drawPixmap(0, 0, mask)
        p.end()
        return out


class MarkdownHighlighter(QSyntaxHighlighter):
    HEADING_SCALE = {1: 2.0, 2: 1.8125, 3: 1.75, 4: 1.525, 5: 1.325, 6: 1.15}
    FENCE = QRegularExpression(r"^\s*(```|~~~)")
    IN_FENCE = 1

    def __init__(self, document):
        super().__init__(document)
        self.base_px = BASE_TEXT_PX
        self.colors = THEMES["light"]
        self._build()

    def configure(self, base_px, colors):
        self.base_px, self.colors = base_px, colors
        self._build()
        self.rehighlight()

    def heading_px(self, level):
        return round(self.base_px * self.HEADING_SCALE[level])

    def _build(self):
        accent = self.colors["accent"]
        self.marker = QTextCharFormat()
        self.marker.setForeground(with_alpha(accent, 0.55))

        italic = QTextCharFormat()
        italic.setFontItalic(True)
        bold = QTextCharFormat()
        bold.setFontWeight(750)

        self.code = QTextCharFormat()
        self.code.setFontFamilies([CODE_FONT, "monospace"])
        self.code.setBackground(with_alpha(accent, 0.22))

        highlight = QTextCharFormat()
        highlight.setBackground(QColor(self.colors["text"]))
        highlight.setForeground(QColor(self.colors["bg"]))

        sub = QTextCharFormat()
        sub.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)
        sup = QTextCharFormat()
        sup.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)

        m = self.marker
        self.rules = [
            (QRegularExpression(r'(?<!\*)(\*)(?!\s)([^*\n]+?)(?<!\s)(\*)(?!\*)'), [m, italic, m]),
            (QRegularExpression(r'(?<!\*)(\*\*)(?!\s)([^*\n]+?)(?<!\s)(\*\*)(?!\*)'), [m, bold, m]),
            (QRegularExpression(r'(?<!`)(`)(?!\s)([^`\n]+?)(?<!\s)(`)(?!`)'), [m, self.code, m]),
            (QRegularExpression(r'(?<![=])(==)(?!\s)([^=\n]+?)(?<!\s)(==)(?![=])'), [m, highlight, m]),
            (QRegularExpression(r'(?<!~)(~)(?!\s)([^~\n]+?)(?<!\s)(~)(?!~)'), [m, sub, m]),
            (QRegularExpression(r'(?<!\^)(\^)(?!\s)([^^\n]+?)(?<!\s)(\^)(?!\^)'), [m, sup, m]),
        ]
        for level in self.HEADING_SCALE:
            px = self.heading_px(level)
            hashes = QTextCharFormat()
            hashes.setFontWeight(800)
            hashes.setForeground(with_alpha(accent, 0.55))
            hashes.setProperty(QTextFormat.Property.FontPixelSize, px)
            text = QTextCharFormat()
            text.setFontWeight(800)
            text.setForeground(QColor(accent))
            text.setProperty(QTextFormat.Property.FontPixelSize, px)
            if level <= 3:  # display sizes read better slightly tightened
                text.setFontLetterSpacingType(QFont.SpacingType.AbsoluteSpacing)
                text.setFontLetterSpacing(-0.02 * px)
            self.rules.append((QRegularExpression(rf'^(#{{{level}}})\s+(.+)$'), [hashes, text]))

    def highlightBlock(self, text):
        in_fence = self.previousBlockState() == self.IN_FENCE
        if self.FENCE.match(text).hasMatch():
            fence = QTextCharFormat(self.marker)
            fence.setFontFamilies([CODE_FONT, "monospace"])
            self.setFormat(0, len(text), fence)
            self.setCurrentBlockState(0 if in_fence else self.IN_FENCE)
            return
        if in_fence:
            self.setFormat(0, len(text), self.code)
            self.setCurrentBlockState(self.IN_FENCE)
            return
        self.setCurrentBlockState(0)
        for pattern, formats in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                for i in range(1, min(match.lastCapturedIndex(), len(formats)) + 1):
                    self.setFormat(match.capturedStart(i), match.capturedLength(i), formats[i - 1])


class Editor(QTextEdit):
    zoom_step = pyqtSignal(int)
    file_dropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptRichText(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.viewport().setAutoFillBackground(False)

    def update_margins(self):
        """Original layout: 12.5 % spacer on each side plus a little padding."""
        side = int(self.width() * SIDE_FRACTION) + SIDE_PAD
        self.setViewportMargins(side, 48, side, 0)

    def resizeEvent(self, event):
        self.update_margins()  # before super(), so the document wraps to the new column
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        # Shift/Ctrl+Enter would insert U+2028 inside the same block, so a heading kept
        # styling the next line (and the file got a real newline anyway). Always split.
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and event.modifiers() & (
                Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier):
            self.textCursor().insertBlock()
            self.ensureCursorVisible()
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta:
                self.zoom_step.emit(1 if delta > 0 else -1)
            event.accept()
            return
        super().wheelEvent(event)

    @staticmethod
    def _local_file(mime):
        files = [u.toLocalFile() for u in mime.urls() if u.isLocalFile()]
        return files[0] if files else None

    def canInsertFromMimeData(self, source):
        return bool(self._local_file(source)) or super().canInsertFromMimeData(source)

    def insertFromMimeData(self, source):
        path = self._local_file(source)
        if path:
            self.file_dropped.emit(path)
        else:
            super().insertFromMimeData(source)


class MarkdownEditor(QMainWindow):
    def __init__(self, open_path=None):
        super().__init__()
        self.settings = QSettings()
        self.current_file = None
        self.theme_mode = self.settings.value("theme", "system")  # no choice yet: follow Windows
        self.zoom = clamp_zoom(int(self.settings.value("zoom", 100)))
        self.motion = system_animations_enabled()

        self.background = CenteredBackground()
        self.editor = Editor()
        self.highlighter = MarkdownHighlighter(self.editor.document())
        self.invert = GlyphInvertEffect(self.background, self.editor.viewport())
        self.editor.viewport().setGraphicsEffect(self.invert)
        self.background.glyphs_moved.connect(self.invert.update)

        layout = QVBoxLayout(self.background)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.editor)
        self.setCentralWidget(self.background)

        self.editor.document().modificationChanged.connect(self.update_title)
        self.editor.zoom_step.connect(self.step_zoom)
        self.editor.file_dropped.connect(self.open_dropped)

        self.create_menu()
        self.create_zoom_shortcuts()
        QGuiApplication.styleHints().colorSchemeChanged.connect(self._system_scheme_changed)

        self.setWindowIcon(QIcon(resource_path("assets/icon.png")))
        self.apply_theme()
        self._set_text("")

        last = self.settings.value("last_file", "")
        target = open_path or (last if last and Path(last).is_file() else None)
        if target:
            self.load_path(target)
        self.update_title()

    # ---- menu and shortcuts -------------------------------------------------
    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        for label, keys, slot in [
            ("New", QKeySequence.StandardKey.New, self.new_file),
            ("Open…", QKeySequence.StandardKey.Open, self.open_file),
            ("Save", QKeySequence.StandardKey.Save, self.save_file),
            ("Save As…", QKeySequence("Ctrl+Shift+S"), self.save_file_as),
        ]:
            action = QAction(label, self, shortcut=keys)
            action.triggered.connect(slot)
            file_menu.addAction(action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        theme_menu = menu.addMenu("Theme")
        group = QActionGroup(self)
        self.theme_actions = {}
        for mode, label in [("light", "Light"), ("dark", "Dark")]:
            action = QAction(label, self, checkable=True)
            action.triggered.connect(lambda _=False, m=mode: self.set_theme_mode(m))
            group.addAction(action)
            theme_menu.addAction(action)
            self.theme_actions[mode] = action

    def create_zoom_shortcuts(self):
        ctrl = Qt.KeyboardModifier.ControlModifier
        keypad = Qt.KeyboardModifier.KeypadModifier
        bindings = [
            (QKeySequence.StandardKey.ZoomIn, 1), (QKeySequence("Ctrl+="), 1),
            (QKeySequence(ctrl | keypad | Qt.Key.Key_Plus), 1),
            (QKeySequence.StandardKey.ZoomOut, -1),
            (QKeySequence(ctrl | keypad | Qt.Key.Key_Minus), -1),
            (QKeySequence("Ctrl+0"), 0), (QKeySequence(ctrl | keypad | Qt.Key.Key_0), 0),
        ]
        for keys, step in bindings:
            shortcut = QShortcut(keys, self)
            shortcut.activated.connect(lambda s=step: self.step_zoom(s))

    # ---- zoom ---------------------------------------------------------------
    def step_zoom(self, step):
        self.set_zoom(100 if step == 0 else self.zoom + step * ZOOM_STEP)

    def set_zoom(self, value):
        value = clamp_zoom(value)
        if value != self.zoom:
            self.zoom = value
            self.settings.setValue("zoom", value)
            self.apply_theme(fade=False)

    def wheelEvent(self, event):
        # Ctrl+wheel over the menu bar or margins scales the same way as over text.
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.angleDelta().y():
            self.step_zoom(1 if event.angleDelta().y() > 0 else -1)
            event.accept()
            return
        super().wheelEvent(event)

    # ---- theme --------------------------------------------------------------
    def resolved_theme(self):
        if self.theme_mode == "system":
            dark = QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
            return "dark" if dark else "light"
        return self.theme_mode if self.theme_mode in THEMES else "light"

    def set_theme_mode(self, mode):
        self.theme_mode = mode
        self.settings.setValue("theme", mode)
        self.apply_theme(fade=True)

    def _system_scheme_changed(self, _scheme):
        if self.theme_mode == "system":
            self.apply_theme(fade=True)

    def apply_theme(self, fade=False):
        def change():
            self.theme_actions[self.resolved_theme()].setChecked(True)
            colors = THEMES[self.resolved_theme()]
            text_px = round(BASE_TEXT_PX * self.zoom / 100)
            self.setStyleSheet(build_qss(colors, text_px, round(BASE_MENU_PX * self.zoom / 100)))
            self.background.set_theme_color(colors["bg"])
            self.invert.color = QColor(colors["bg"])
            self.highlighter.configure(text_px, colors)
            self.editor.update_margins()
            self.invert.update()

        if fade and self.motion and self.isVisible():
            self._crossfade(change)
        else:
            change()

    def _crossfade(self, change):
        shot = QLabel(self)
        shot.setPixmap(self.grab())
        shot.setGeometry(self.rect())
        shot.show()
        shot.raise_()
        change()
        effect = QGraphicsOpacityEffect(shot)
        shot.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", shot)
        anim.setDuration(180)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(shot.deleteLater)
        anim.start()

    # ---- layout -------------------------------------------------------------
    def showEvent(self, event):
        super().showEvent(event)
        if self.motion and not getattr(self, "_animated", False):
            self._animated = True
            QTimer.singleShot(0, self.background.animate_in)

    # ---- documents ----------------------------------------------------------
    def _set_text(self, text):
        self.editor.setPlainText(text)
        cursor = QTextCursor(self.editor.document())
        cursor.select(QTextCursor.SelectionType.Document)
        block = QTextBlockFormat()
        block.setLineHeight(120, QTextBlockFormat.LineHeightTypes.ProportionalHeight.value)
        cursor.mergeBlockFormat(block)
        self.editor.document().clearUndoRedoStacks()
        self.editor.document().setModified(False)
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)

    def update_title(self, *_):
        name = Path(self.current_file).name if self.current_file else "Untitled"
        dot = " •" if self.editor.document().isModified() else ""
        self.setWindowTitle(f"{name}{dot} — UpNote")

    def maybe_save(self):
        if not self.editor.document().isModified():
            return True
        name = Path(self.current_file).name if self.current_file else "Untitled"
        buttons = (QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard
                   | QMessageBox.StandardButton.Cancel)
        answer = QMessageBox.question(self, "UpNote", f"Save changes to {name}?", buttons,
                                      QMessageBox.StandardButton.Save)
        if answer == QMessageBox.StandardButton.Save:
            return self.save_file()
        return answer == QMessageBox.StandardButton.Discard

    def new_file(self):
        if self.maybe_save():
            self.current_file = None
            self._set_text("")
            self.update_title()

    def load_path(self, path):
        try:
            text = Path(path).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as error:
            QMessageBox.warning(self, "UpNote", f"Couldn't open {Path(path).name}.\n\n{error}")
            return False
        self.current_file = str(path)
        self._set_text(text)
        self.settings.setValue("last_file", self.current_file)
        self.update_title()
        return True

    def open_file(self):
        if not self.maybe_save():
            return
        path, _ = QFileDialog.getOpenFileName(self, "Open Markdown File", "", FILE_FILTER)
        if path:
            self.load_path(path)

    def open_dropped(self, path):
        if self.maybe_save():
            self.load_path(path)

    def _write(self, path):
        try:
            Path(path).write_text(self.editor.toPlainText(), encoding="utf-8")
        except OSError as error:
            QMessageBox.warning(self, "UpNote", f"Couldn't save {Path(path).name}.\n\n{error}")
            return False
        self.current_file = str(path)
        self.settings.setValue("last_file", self.current_file)
        self.editor.document().setModified(False)
        self.update_title()
        return True

    def save_file(self):
        return self._write(self.current_file) if self.current_file else self.save_file_as()

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Markdown File", "", FILE_FILTER)
        return self._write(path) if path else False

    def closeEvent(self, event):
        if not self.maybe_save():
            event.ignore()
            return
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("UpNote")
    app.setApplicationName("UpNote")
    open_path = next((a for a in sys.argv[1:] if not a.startswith("-")), None)
    window = MarkdownEditor(open_path)
    geometry = window.settings.value("geometry")
    if geometry is not None and window.restoreGeometry(geometry):
        window.show()
    else:
        window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
