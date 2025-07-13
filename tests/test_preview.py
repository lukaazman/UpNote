import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QEventLoop
from upnote import MarkdownEditor


def wait_for_load(view):
    loop = QEventLoop()
    view.loadFinished.connect(loop.quit)
    loop.exec()


def get_page_html(page):
    loop = QEventLoop()
    html_container = {}

    def callback(html):
        html_container['html'] = html
        loop.quit()

    page.toHtml(callback)
    loop.exec()
    return html_container['html']


def setup_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_preview_light_and_dark():
    app = setup_app()
    editor = MarkdownEditor()
    editor.editor.setPlainText('# Title')
    editor.update_preview()
    wait_for_load(editor.preview)

    light_html = get_page_html(editor.preview.page())
    assert '<h1>Title</h1>' in light_html
    assert 'background-color: white' in light_html

    editor.toggle_theme()
    editor.update_preview()
    wait_for_load(editor.preview)

    dark_html = get_page_html(editor.preview.page())
    assert '<h1>Title</h1>' in dark_html
    assert 'background-color: #2e2e2e' in dark_html

    editor.close()
