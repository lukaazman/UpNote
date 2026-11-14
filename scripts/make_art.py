"""Generate UpNote artwork: background glyph layers and the app icon.

Run from anywhere:  python scripts/make_art.py
Outputs into assets/: mark-arrow.png, mark-n.png (transparent, same canvas so
they stack), icon.png (512 px) and icon.ico (16-256 px, PNG-compressed).
"""
import random
import struct
import sys
from pathlib import Path

from PyQt6.QtCore import QBuffer, QIODevice, QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath, QPen,
)

ASSETS = Path(__file__).resolve().parent.parent / "assets"
PINK = QColor("#f745e0")
CYAN = QColor("#45f1f7")

# Glyph geometry in units of glyph height (H = 1.0).
ARROW_W, HEAD_H, STEM_W = 0.86, 0.47, 0.30
N_W, N_STROKE = 0.86, 0.29
GAP = 0.34
STREAK_ROOM = 0.34


def arrow_path(x, y, h):
    w, hh, sw = ARROW_W * h, HEAD_H * h, STEM_W * h
    cx = x + w / 2
    p = QPainterPath(QPointF(cx, y))
    p.lineTo(x + w, y + hh)
    p.lineTo(cx + sw / 2, y + hh)
    p.lineTo(cx + sw / 2, y + h)
    p.lineTo(cx - sw / 2, y + h)
    p.lineTo(cx - sw / 2, y + hh)
    p.lineTo(x, y + hh)
    p.closeSubpath()
    return p


def n_path(x, y, h):
    w, s = N_W * h, N_STROKE * h
    p = QPainterPath(QPointF(x, y))
    p.lineTo(x + s, y)
    p.lineTo(x + w - s, y + h * 0.62)
    p.lineTo(x + w - s, y)
    p.lineTo(x + w, y)
    p.lineTo(x + w, y + h)
    p.lineTo(x + w - s, y + h)
    p.lineTo(x + s, y + h * 0.38)
    p.lineTo(x + s, y + h)
    p.lineTo(x, y + h)
    p.closeSubpath()
    return p


def blank(w, h):
    img = QImage(int(w), int(h), QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    return img


def draw_glyph(img, path, color, ghost, h, seed):
    """Fill the glyph, a faint chromatic ghost, and horizontal motion streaks
    trailing from its right-hand edges (the motion reads left-to-right/up)."""
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    ghost_c = QColor(ghost)
    ghost_c.setAlphaF(0.45)
    p.fillPath(path.translated(-h * 0.012, h * 0.012), ghost_c)
    p.fillPath(path, color)
    p.end()

    # Streaks start at the rightmost covered pixel of each scanline.
    rng = random.Random(seed)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    top, bottom = int(path.boundingRect().top()), int(path.boundingRect().bottom())
    step = max(1.0, h / 140)
    y = float(top)
    while y < bottom:
        row = int(y)
        edge = None
        for x in range(img.width() - 1, -1, -1):
            if img.pixelColor(x, row).alpha() > 200:
                edge = x
                break
        if edge is not None and rng.random() < 0.82:
            length = h * STREAK_ROOM * rng.random() ** 1.6
            grad = QLinearGradient(edge - 2, 0, edge + length, 0)
            head = QColor(color)
            head.setAlphaF(0.85)
            tail = QColor(color)
            tail.setAlpha(0)
            grad.setColorAt(0, head)
            grad.setColorAt(1, tail)
            p.setPen(QPen(grad, step * rng.uniform(0.45, 0.9)))
            p.drawLine(QPointF(edge - 2, y), QPointF(edge + length, y))
        y += step * rng.uniform(0.9, 1.6)
    p.end()


def mark_layers(h):
    pad = h * 0.1
    w = pad * 2 + ARROW_W * h + GAP * h + N_W * h + STREAK_ROOM * h
    hgt = pad * 2 + h
    arrow, n = blank(w, hgt), blank(w, hgt)
    draw_glyph(arrow, arrow_path(pad, pad, h), PINK, CYAN, h, 7)
    draw_glyph(n, n_path(pad + (ARROW_W + GAP) * h, pad, h), CYAN, PINK, h, 11)
    return arrow, n


def icon(size):
    img = blank(size, size)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.fillRect(QRectF(0, 0, size, size), QColor("white"))
    arrow, n = mark_layers(size * 0.3)
    target_w = size * 0.9
    scale = target_w / arrow.width()
    tw, th = arrow.width() * scale, arrow.height() * scale
    dst = QRectF((size - tw) / 2 + size * 0.03, (size - th) / 2, tw, th)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    p.drawImage(dst, arrow)
    p.drawImage(dst, n)
    p.end()
    return img


def png_bytes(img):
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    img.save(buf, "PNG")
    return bytes(buf.data())


def write_ico(path, base):
    sizes = [256, 128, 64, 48, 32, 16]
    blobs = [png_bytes(base.scaled(s, s, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)) for s in sizes]
    header = struct.pack("<HHH", 0, 1, len(sizes))
    offset = 6 + 16 * len(sizes)
    entries = b""
    for s, blob in zip(sizes, blobs):
        entries += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    path.write_bytes(header + entries + b"".join(blobs))


def main():
    app = QGuiApplication(sys.argv)  # noqa: F841 - QPainter on text/paths needs a GUI app
    ASSETS.mkdir(exist_ok=True)
    arrow, n = mark_layers(360)
    arrow.save(str(ASSETS / "mark-arrow.png"))
    n.save(str(ASSETS / "mark-n.png"))
    big = icon(512)
    big.save(str(ASSETS / "icon.png"))
    write_ico(ASSETS / "icon.ico", big)
    print("wrote", *sorted(p.name for p in ASSETS.iterdir()))


if __name__ == "__main__":
    main()
