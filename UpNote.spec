# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project_dir = Path(SPEC).parent

a = Analysis(
    [str(project_dir / "upnote.py")], pathex=[str(project_dir)], binaries=[],
    datas=[(str(project_dir / "background.png"), "."), (str(project_dir / "icon.png"), ".")],
    hiddenimports=["markdown.extensions.extra", "markdown.extensions.sane_lists"],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="UpNote", debug=False,
         bootloader_ignore_signals=False, strip=False, upx=True, console=False,
         icon=str(project_dir / "icon.png"))