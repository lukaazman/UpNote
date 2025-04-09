import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QFileDialog
)
from PyQt6.QtGui import QAction, QIcon, QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QRegularExpression
import markdown

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        syntax_format = QTextCharFormat()
        syntax_format.setForeground(QColor('#45f1f7'))

        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression(r'(\*)([^*\n]+)(\*)'), [syntax_format, italic_format, syntax_format]))

        bold_format = QTextCharFormat()
        bold_format.setFontWeight(750)
        self.highlighting_rules.append((QRegularExpression(r'(\*\*)([^*\n]+)(\*\*)'), [syntax_format, bold_format, syntax_format]))

        code_format = QTextCharFormat()
        code_format.setBackground(QColor('#45f1f7'))
        code_format.setFontFamily('Consolas')
        self.highlighting_rules.append((QRegularExpression(r'(`)([^`\n]+)(`)'), [syntax_format, code_format, syntax_format]))

        heading_format = QTextCharFormat()
        heading_format.setFontWeight(800)
        heading_format.setForeground(QColor('#45f1f7'))
        self.highlighting_rules.append((QRegularExpression(r'^(#{1,6})\s+(.+)$'), [heading_format, heading_format]))

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor('#f745e0'))
        highlight_format.setForeground(QColor('#ffffff'))
        self.highlighting_rules.append((QRegularExpression(r'(==)([^=\n]+)(==)'), [syntax_format, highlight_format, syntax_format]))

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
            QTextEdit {
                background: url(background.png) no-repeat center center;
                color: #f745e0;
                font-size: 15px;
                font-family: Arial;
                border: none;
            }
        """)

        self.editor.textChanged.connect(self.update_preview)

        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        layout.addWidget(self.preview)

        container = QWidget()
        container.setLayout(layout)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(container)

        self.create_menu()

        self.setWindowTitle("UpNote")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(1280, 720)
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

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_light_theme(self):
        self.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #f745e0;
                font-size: 15px;
                font-family: Arial;
                border: none;
            }
            QMenuBar {
                background-color: #f0f0f0;
                color: #333;
            }
            QMenu {
                background-color: #f0f0f0;
                color: #f745e0;
                border: 1px solid #ccc;
            }
            QMenu::item:selected {
                background-color: #c256fc;
                color: white;
            }
            QWidget {
                background-color: white;
            }
        """)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QTextEdit {
                background-color: #2e2e2e;
                color: #f745e0;
                font-size: 15px;
                font-family: Arial;
                border: none;
            }
            QMenuBar {
                background-color: #3c3c3c;
                color: white;
            }
            QMenu {
                background-color: #3c3c3c;
                color: #f745e0;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #c256fc;
                color: white;
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
                        line-height: 1.6;
                        padding: 20px;
                        max-width: 800px;
                        margin: 0 auto;
                        color: #f745e0;
                        background-color: {"#2e2e2e" if self.dark_mode else "white"};
                    }}
                    pre {{
                        background-color: #f0f0f0;
                        padding: 10px;
                        border-radius: 3px;
                        overflow-x: auto;
                    }}
                    code {{
                        font-family: Courier, monospace;
                        background-color: #f0f0f0;
                        padding: 2px 4px;
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
