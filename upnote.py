import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QFileDialog, 
    QHBoxLayout, QFrame
)
from PyQt6.QtGui import QAction, QIcon, QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QRegularExpression, Qt
import markdown

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        syntax_format = QTextCharFormat()
        syntax_format.setForeground(QColor('#45f1f7'))

        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((
            QRegularExpression(r'(?<!\*)(\*)(?!\s)([^*\n]+?)(?<!\s)(\*)(?!\*)'),
            [syntax_format, italic_format, syntax_format]
        ))


        bold_format = QTextCharFormat()
        bold_format.setFontWeight(750)
        self.highlighting_rules.append((
            QRegularExpression(r'(?<!\*)(\*\*)(?!\s)([^*\n]+?)(?<!\s)(\*\*)(?!\*)'),
            [syntax_format, bold_format, syntax_format]
        ))


        code_format = QTextCharFormat()
        code_format.setBackground(QColor('#45f1f7'))
        code_format.setFontFamily('Consolas')
        self.highlighting_rules.append((
            QRegularExpression(r'(?<!`)(`)(?!\s)([^`\n]+?)(?<!\s)(`)(?!`)'),
            [syntax_format, code_format, syntax_format]
        ))

        heading_styles = [
        (1, 2.0),      # h1
        (2, 1.8125),   # h2
        (3, 1.75),     # h3
        (4, 1.525),    # h4
        (5, 1.325),    # h5
        (6, 1.15)      # h6
        ]

        for level, size in heading_styles:
            pattern = QRegularExpression(rf'^(#{{{level}}})\s+(.+)$')
            hash_format = QTextCharFormat()
            hash_format.setFontWeight(800)
            hash_format.setForeground(QColor('#45f1f7'))

            text_format = QTextCharFormat()
            text_format.setFontWeight(800)
            text_format.setForeground(QColor('#45f1f7'))
            # font size scaled from a 30 pt base
            text_format.setFontPointSize(size * 30)

            self.highlighting_rules.append((pattern, [hash_format, text_format]))

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor('#f745e0'))
        highlight_format.setForeground(QColor('#ffffff'))
        self.highlighting_rules.append((
            QRegularExpression(
                r'(?<![=])(==)(?!\s)([^=\n]+?)(?<!\s)(==)(?![=])'
            ),
            [syntax_format, highlight_format, syntax_format]
        ))


        subscript_format = QTextCharFormat()
        subscript_format.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)
        self.highlighting_rules.append((
            QRegularExpression(
                r'(?<!~)(~)(?!\s)([^~\n]+?)(?<!\s)(~)(?!~)'
            ),
            [syntax_format, subscript_format, syntax_format]
        ))


        superscript_format = QTextCharFormat()
        superscript_format.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)
        self.highlighting_rules.append((
            QRegularExpression(
                r'(?<!\^)(\^)(?!\s)([^^\n]+?)(?<!\s)(\^)(?!\^)'
            ),
            [syntax_format, superscript_format, syntax_format]
        ))

    def highlightBlock(self, text):
        for pattern, formats in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                for i in range(1, match.lastCapturedIndex() + 1):
                    if i <= len(formats):
                        self.setFormat(match.capturedStart(i), match.capturedLength(i), formats[i-1])

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_file = None
        self.dark_mode = False

        self.editor = QTextEdit()
        self.preview = QWebEngineView()
        self.highlighter = MarkdownHighlighter(self.editor.document())

        self.editor.setStyleSheet("""
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
            }
        """)

        self.editor.textChanged.connect(self.update_preview)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        editor_container = QHBoxLayout()
        editor_container.setContentsMargins(0, 40, 0, 40)

        left_spacer = QFrame()
        left_spacer.setFixedWidth(int(self.width() * 0.125))
        editor_container.addWidget(left_spacer)

        editor_container.addWidget(self.editor, 75)

        right_spacer = QFrame()
        right_spacer.setFixedWidth(int(self.width() * 0.125))
        editor_container.addWidget(right_spacer)

        preview_container = QHBoxLayout()
        preview_container.setContentsMargins(0, 0, 0, 0)
        preview_container.addWidget(self.preview)

        main_layout.addLayout(editor_container)
        main_layout.addLayout(preview_container)

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)

        self.create_menu()

        self.setWindowTitle("UpNote")
        self.setWindowIcon(QIcon("icon.png"))
        self.showMaximized()
        self.apply_light_theme()

    def create_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        theme_action = QAction("Theme", self)
        theme_action.triggered.connect(self.toggle_theme)
        menu.addAction(theme_action)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = self.width()
        left_right_width = int(width * 0.125)
        layout = self.centralWidget().layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            child_layout = item.layout()
            if isinstance(child_layout, QHBoxLayout) and child_layout.count() > 2:
                child_layout.itemAt(0).widget().setFixedWidth(left_right_width)
                child_layout.itemAt(2).widget().setFixedWidth(left_right_width)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
        self.update_preview()

    def apply_light_theme(self):
        self.setStyleSheet("""
            QTextEdit {
                background: url(background.png) no-repeat center center;
                background-color: white;
                color: #f745e0;
                font-size: 30px;
                font-family: Arial;
                line-height: 5.4;
                border: none;
                padding: 40px;
            }
            QMenuBar {
                background-color: #f0f0f0;
                color: #f745e0;
            }
            QMenuBar::selected {
                color:#45f1f7;
                backgound-color: #f745e0;
            }
            QMenu {
                background-color: #f0f0f0;
                color: #f745e0;
            }
            QMenu::item:selected {
                background-color: #45f1f7;
                color: white;
            }
            QWidget {
                background-color: white;
            }
        """)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QTextEdit {
                background: url(background.png) no-repeat center center;
                background-color: #2e2e2e;
                color: #f745e0;
                font-size: 30px;
                font-family: Arial;
                line-height: 5.4;
                border: none;
                padding: 40px;
            }
            QMenuBar {
                background-color: #3c3c3c;
                color: #45f1f7;
            }
            QMenuBar::selected {
                color:#f745e0;
                background-color: #45f1f7;
            }
            QMenu {
                background-color: #3c3c3c;
                color: #45f1f7;
            }
            QMenu::item:selected {
                background-color: #f745e0;
                color: black;
            }
            QWidget {
                background-color: #2e2e2e;
            }
        """)

    def update_preview(self):
        html = markdown.markdown(self.editor.toPlainText())
        self.preview.setHtml(f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 4.8;
                        padding: 40px;
                        max-width: 75%;
                        margin: 40px auto;
                        color: #f745e0;
                        background-color: {"#2e2e2e" if self.dark_mode else "white"};
                        font-size: 30px;
                    }}
                    pre {{
                        background-color: #f0f0f0;
                        padding: 20px;
                        border-radius: 3px;
                        overflow-x: auto;
                    }}
                    code {{
                        font-family: Courier, monospace;
                        background-color: #f0f0f0;
                        padding: 5px 10px;
                        border-radius: 3px;
                    }}
                </style>
            </head>
            <body>{html}</body>
        </html>
        """)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Markdown File", "", "Markdown Files (*.md *.markdown);;All Files (*)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.editor.setPlainText(file.read())
            self.current_file = file_path

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as file:
                file.write(self.editor.toPlainText())
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Markdown File", "", "Markdown Files (*.md *.markdown);;All Files (*)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.editor.toPlainText())
            self.current_file = file_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownEditor()
    window.show()
    sys.exit(app.exec())