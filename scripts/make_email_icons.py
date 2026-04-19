#!/usr/bin/env python3
"""Małe PNG 18x18 dla stopki mailowej (Outlook często usuwa SVG)."""
import math
import struct
import zlib
from pathlib import Path

W = H = 18
PINK = (0xEC, 0x48, 0x99)
WHITE = (255, 255, 255)


def line_near(x, y, x0, y0, x1, y1, thick):
    dx, dy = x1 - x0, y1 - y0
    if dx * dx + dy * dy == 0:
        return math.hypot(x - x0, y - y0) <= thick
    t = max(0, min(1, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy)))
    px, py = x0 + t * dx, y0 + t * dy
    return math.hypot(x - px, y - py) <= thick


def write_png_rgb(path: Path, pixel_fn):
    rows = []
    for y in range(H):
        row = b"\x00"
        for x in range(W):
            row += bytes(pixel_fn(x, y))
        rows.append(row)
    raw = b"".join(rows)
    compressed = zlib.compress(raw, 9)

    def piece(t, data):
        return struct.pack(">I", len(data)) + t + data + struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = sig + piece(b"IHDR", ihdr) + piece(b"IDAT", compressed) + piece(b"IEND", b"")
    path.write_bytes(data)


def phone(x, y):
    # obrys słuchawki
    d = math.hypot(x - 12, y - 6)
    if 2.4 <= d <= 4.1:
        return PINK
    if 6 <= x <= 10 and 7 <= y <= 12:
        return PINK
    if 8 <= x <= 14 and 11 <= y <= 14:
        return PINK
    if math.hypot(x - 6, y - 13) <= 2.2:
        return PINK
    return WHITE


def envelope(x, y):
    if 4 <= x <= 14 and (y == 5 or y == 13):
        return PINK
    if (x == 4 or x == 14) and 5 <= y <= 13:
        return PINK
    if line_near(x, y, 4, 5, 9, 9, 1.0) or line_near(x, y, 14, 5, 9, 9, 1.0):
        return PINK
    return WHITE


def globe(x, y):
    d = math.hypot(x - 9, y - 9)
    if 6.3 <= d <= 7.3:
        return PINK
    if abs(x - 9) < 0.55 and 3 <= y <= 15:
        return PINK
    if abs(y - 9) < 0.55 and 3 <= x <= 15:
        return PINK
    return WHITE


def main():
    assets = Path(__file__).resolve().parent.parent / "assets"
    assets.mkdir(exist_ok=True)
    write_png_rgb(assets / "icon-phone.png", lambda x, y: phone(x, y))
    write_png_rgb(assets / "icon-email.png", lambda x, y: envelope(x, y))
    write_png_rgb(assets / "icon-web.png", lambda x, y: globe(x, y))
    print("OK:", assets / "icon-phone.png")


if __name__ == "__main__":
    main()
