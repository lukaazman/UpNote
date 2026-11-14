# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path(SPEC).parent.parent
assets = root / "assets"

# Only QtCore/QtGui/QtWidgets are used; keep the rest of Qt out of the bundle.
UNUSED_QT = [
    "PyQt6.QtNetwork", "PyQt6.QtQml", "PyQt6.QtQuick", "PyQt6.QtPdf", "PyQt6.QtSvg",
    "PyQt6.QtOpenGL", "PyQt6.QtOpenGLWidgets", "PyQt6.QtMultimedia", "PyQt6.QtSql",
    "PyQt6.QtTest", "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineWidgets", "PyQt6.QtDBus",
    "PyQt6.QtBluetooth", "PyQt6.QtPositioning", "PyQt6.QtSensors", "PyQt6.QtSerialPort",
    "PyQt6.QtPrintSupport", "PyQt6.QtDesigner", "PyQt6.QtHelp", "PyQt6.QtXml",
]
DROP_FILES = ("opengl32sw.dll", "d3dcompiler", "qt6pdf", "qt6qml", "qt6quick", "qt6network",
              "qt6svg", "qt6opengl", "qt6virtualkeyboard", "qsvg", "qpdf", "qtvirtualkeyboard",
              "qnetworklistmanager", "qtuiotouchplugin", "qcertonlybackend", "qschannelbackend",
              "qopensslbackend")

a = Analysis(
    [str(root / "upnote.py")], pathex=[str(root)], binaries=[],
    datas=[(str(p), "assets") for p in assets.glob("*.png")],
    hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=UNUSED_QT + ["tkinter", "unittest", "pydoc", "email", "http", "xml", "sqlite3"],
    noarchive=False,
)
a.binaries = [b for b in a.binaries if not any(k in b[0].lower() for k in DROP_FILES)]
a.datas = [d for d in a.datas if "translations" not in d[0].replace("\\", "/")]

pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="UpNote", debug=False,
          bootloader_ignore_signals=False, strip=False, upx=False, console=False,
          icon=str(assets / "icon.ico"))
