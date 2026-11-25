#!/usr/bin/env python3
"""The World in One Page - Wednesday 25 November 2026.

Draws a one-page cream broadsheet that sums up the world news of
25 November 2026 and writes it to /output/entry.png (or to
$MAKEFUN_OUTPUT_DIR/entry.png when that variable is set).

Pure Python standard library: a hand-made 5x7 pixel font, flat-shape
drawings rasterised onto an RGB framebuffer, and a from-scratch PNG
encoder built on zlib/struct. No network, no randomness, no clock:
two runs write the same bytes.
"""

import os
import struct
import zlib

W = 1024
H = 1024

CREAM = (247, 242, 228)
PAPER_EDGE = (238, 231, 210)
INK = (24, 22, 18)
SOFT_INK = (74, 68, 58)
RED = (168, 30, 24)
BLUE = (30, 62, 110)
TEAL = (18, 96, 92)
GOLD = (176, 128, 20)
GREY = (120, 114, 100)
SMOKE = (168, 160, 144)
SKY = (214, 222, 228)
SEA = (52, 96, 128)

# ---------------------------------------------------------------- font
# 5x7 pixel glyphs, seven rows of five bits, most significant bit left.
FONT = {
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x0E, 0x11, 0x01, 0x06, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "%": (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x03),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "*": (0x00, 0x15, 0x0E, 0x15, 0x00, 0x00, 0x00),
}

# ------------------------------------------------------- framebuffer

FB = bytearray(W * H * 3)


def fill_rect(x, y, w, h, colour):
    if w <= 0 or h <= 0:
        return
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(colour) * (x1 - x0)
    for yy in range(y0, y1):
        off = (yy * W + x0) * 3
        FB[off:off + len(row)] = row


def px(x, y, colour):
    if 0 <= x < W and 0 <= y < H:
        off = (y * W + x) * 3
        FB[off] = colour[0]
        FB[off + 1] = colour[1]
        FB[off + 2] = colour[2]


def disc(cx, cy, r, colour):
    r2 = r * r
    for yy in range(cy - r, cy + r + 1):
        dy = yy - cy
        for xx in range(cx - r, cx + r + 1):
            dx = xx - cx
            if dx * dx + dy * dy <= r2:
                px(xx, yy, colour)


def line(x0, y0, x1, y1, colour, thick=1):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    half = thick // 2
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i // steps
        y = y0 + (y1 - y0) * i // steps
        fill_rect(x - half, y - half, thick, thick, colour)


def outline_rect(x, y, w, h, colour, thick=2):
    fill_rect(x, y, w, thick, colour)
    fill_rect(x, y + h - thick, w, thick, colour)
    fill_rect(x, y, thick, h, colour)
    fill_rect(x + w - thick, y, thick, h, colour)


# ---------------------------------------------------------------- text

def text_w(s, scale):
    return len(s) * 6 * scale


def draw_text(x, y, s, scale, colour):
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for r in range(7):
            bits = glyph[r]
            for c in range(5):
                if bits & (0x10 >> c):
                    fill_rect(x + c * scale, y + r * scale, scale, scale, colour)
        x += 6 * scale
    return x


def draw_centered(cx, y, s, scale, colour):
    return draw_text(cx - text_w(s, scale) // 2, y, s, scale, colour)


def wrap(s, scale, max_w):
    words = s.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_paragraph(x, y, s, scale, colour, max_w, leading=None):
    if leading is None:
        leading = 9 * scale
    for ln in wrap(s, scale, max_w):
        draw_text(x, y, ln, scale, colour)
        y += leading
    return y


# ------------------------------------------------------------ drawings

def draw_skyline(x, y, w, h):
    """Riyadh skyline: low blocks, one tall tower, a burst, smoke."""
    fill_rect(x, y, w, h, SKY)
    ground = y + h - 26
    # distant blocks
    for bx, bw, bh in ((6, 52, 44), (66, 38, 62), (470, 56, 50),
                       (534, 40, 70), (110, 44, 34)):
        fill_rect(x + bx, ground - bh, bw, bh, (148, 156, 164))
    # near blocks
    for bx, bw, bh in ((18, 64, 58), (404, 70, 66), (486, 62, 44),
                       (300, 54, 40)):
        fill_rect(x + bx, ground - bh, bw, bh, (96, 102, 110))
    # the tall tower
    tx = x + w // 2 - 26
    fill_rect(tx, y + 18, 52, ground - y - 18, (52, 58, 66))
    fill_rect(tx + 22, y + 6, 8, 14, (52, 58, 66))
    for wy in range(y + 30, ground - 12, 14):
        for wx in range(tx + 7, tx + 44, 12):
            fill_rect(wx, wy, 6, 7, (196, 205, 214))
    # impact burst on the tower's upper third
    cx, cy = tx + 52, y + 52
    for r, col in ((26, (240, 178, 60)), (17, (232, 110, 40)),
                   (9, RED)):
        disc(cx, cy, r, col)
    for dx, dy in ((34, 0), (-30, 10), (24, -22), (10, 26), (-8, -30),
                   (30, 20), (-26, -16)):
        line(cx, cy, cx + dx, cy + dy, (232, 110, 40), 3)
    # smoke drifting up-right
    for sx, sy, sr in ((cx + 30, cy - 26, 12), (cx + 52, cy - 40, 16),
                       (cx + 80, cy - 52, 20), (cx + 112, cy - 60, 15)):
        disc(sx, sy, sr, SMOKE)
    fill_rect(x, ground, w, 3, INK)
    fill_rect(x, y + h - 23, w, 23, (228, 220, 196))
    draw_text(x + 10, y + h - 18, "RIYADH'S FINANCIAL DISTRICT",
              2, SOFT_INK)


def draw_tanker(x, y, w, h):
    """A tanker on a mined strait."""
    fill_rect(x, y, w, h, SKY)
    sea_y = y + h - 44
    fill_rect(x, sea_y, w, h - (sea_y - y), SEA)
    for i in range(26):
        wx = x + (i * 37) % w
        wy = sea_y + 8 + (i * 13) % 26
        fill_rect(wx, wy, 18, 3, (120, 165, 195))
    hx = x + 26
    hy = sea_y - 30
    fill_rect(hx, hy, w - 70, 16, (40, 44, 50))          # hull
    fill_rect(hx + w - 70, hy + 4, 18, 12, (40, 44, 50))  # bow taper
    fill_rect(hx + 8, hy - 12, 30, 12, (214, 208, 192))   # bridge block
    fill_rect(hx + 16, hy - 22, 8, 10, INK)               # funnel
    for i, col in enumerate((RED, GOLD, TEAL, BLUE)):
        fill_rect(hx + 52 + i * 34, hy - 11, 28, 11, col)  # tank domes
    # mine: spiked disc in the water ahead of the bow
    mx, my = hx + w - 48, sea_y + 16
    disc(mx, my, 9, INK)
    for dx, dy in ((12, 0), (-12, 0), (0, -12), (8, 8), (-8, -8)):
        line(mx, my, mx + dx, my + dy, INK, 3)
    # small burst in the water astern, where a mine has gone off
    bx, by = hx - 14, sea_y + 12
    for r, col in ((11, (240, 178, 60)), (6, RED)):
        disc(bx, by, r, col)


def draw_rocket(x, y, w, h):
    """A rocket climbing past a crescent moon."""
    fill_rect(x, y, w, h, (28, 40, 66))
    for i in range(40):
        sx = x + (i * 53) % w
        sy = y + (i * 29) % (h - 20)
        fill_rect(sx, sy, 3, 3, (210, 218, 230))
    disc(x + w - 44, y + 34, 17, (226, 222, 200))
    disc(x + w - 34, y + 28, 15, (28, 40, 66))
    cx = x + w // 2
    top = y + 26
    fill_rect(cx - 13, top + 22, 26, 74, (226, 224, 216))  # body
    for i in range(13):                                     # nose cone
        fill_rect(cx - 13 + i, top + i, 26 - 2 * i, 2, RED)
    fill_rect(cx - 13, top + 48, 26, 7, RED)                # band
    disc(cx, top + 36, 5, BLUE)                             # porthole
    fill_rect(cx - 25, top + 74, 12, 24, RED)               # fins
    fill_rect(cx + 13, top + 74, 12, 24, RED)
    for i, col in enumerate(((240, 178, 60), (232, 110, 40))):
        r = 12 - i * 5
        disc(cx, top + 104 + i * 4, r, col)                 # flame
    draw_text(x + 10, y + h - 20, "SHENZHOU-24", 2, (200, 208, 220))


def draw_chart(x, y, w, h):
    """A falling share-price line, scaled to fit its panel."""
    fill_rect(x, y, w, h, (240, 236, 222))
    gx, gy = x + 16, y + h - 8
    line(gx, y + 6, gx, gy, GREY, 2)
    line(gx, gy, x + w - 10, gy, GREY, 2)
    raw = [(0, 8), (34, 14), (62, 10), (92, 30), (120, 26),
           (150, 52), (182, 66), (212, 62), (244, 92), (268, 104)]
    span_x = max(w - 44, 1)
    span_y = max(h - 22, 1)
    pts = [(gx + dx * span_x // 268, y + 8 + dy * span_y // 104)
           for dx, dy in raw]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        line(ax, ay, bx, by, RED, 4)
    lx, ly = pts[-1]
    for dx, dy in ((9, 1), (1, 9), (10, 10)):
        line(lx, ly, lx + dx, ly + dy, RED, 3)


# -------------------------------------------------------------- layout

def box(x, y, w, h, kicker, kicker_colour=RED):
    outline_rect(x, y, w, h, INK, 2)
    fill_rect(x, y, w, 24, INK)
    draw_text(x + 10, y + 5, kicker, 2, CREAM)
    return y + 34


def headline_block(x, y, s, scale, colour, max_w):
    """Draw a wrapped headline; return the y just below it."""
    leading = 9 * scale
    for ln in wrap(s, scale, max_w):
        draw_text(x, y, ln, scale, colour)
        y += leading
    return y


def build():
    fill_rect(0, 0, W, H, CREAM)
    fill_rect(0, 0, W, 10, INK)
    fill_rect(0, H - 10, W, 10, INK)

    # masthead
    draw_centered(W // 2, 30, "THE WORLD IN ONE PAGE", 7, INK)
    draw_centered(W // 2, 92,
                  "EVERY STORY HERE HAPPENED - OR WAS FIRST REPORTED - "
                  "ON THE DAY BELOW", 2, SOFT_INK)
    fill_rect(36, 122, W - 72, 3, INK)
    # date bar
    fill_rect(36, 134, W - 72, 46, INK)
    draw_centered(W // 2, 143, "WEDNESDAY 25 NOVEMBER 2026", 4, CREAM)
    fill_rect(36, 188, W - 72, 3, INK)

    # ---- lead story, left
    lx, lw = 36, 628
    draw_text(lx, 198, "SAUDI ARABIA - THE LEAD", 2, RED)
    draw_text(lx, 218, "HOUTHIS HIT RIYADH'S", 5, INK)
    draw_text(lx, 256, "TALLEST TOWER AGAIN", 5, INK)
    draw_skyline(lx, 300, lw, 164)
    draw_paragraph(
        lx, 476,
        "Yemen's Houthis struck the Saudi capital's tallest skyscraper "
        "for the second time in less than a week, injuring 11 people "
        "in the financial district. Riyadh called it a terrorist "
        "attack; the strike widens a war already spilling across the "
        "region's skies and sea lanes.", 2, INK, lw)

    # ---- right rail: Hormuz, then Nvidia
    rx, rw = 688, 300
    cy = box(rx, 198, rw, 232, "STRAIT OF HORMUZ")
    draw_tanker(rx + 10, cy, rw - 20, 86)
    draw_paragraph(rx + 12, cy + 96,
                   "Two tankers hit mines in the strait, Tehran said "
                   "- explosions at the world's oil chokepoint.",
                   2, INK, rw - 24)
    cy = box(rx, 446, rw, 150, "MARKETS - NVIDIA", BLUE)
    draw_chart(rx + 10, cy, rw - 20, 50)
    draw_paragraph(rx + 12, cy + 58,
                   "The 7% fall came as lawmakers questioned Huang's "
                   "return.", 2, INK, rw - 24)

    fill_rect(36, 610, W - 72, 3, INK)

    # ---- three boxes
    bw = (W - 72 - 32) // 3
    by, bh = 626, 190
    cy = box(36, by, bw, bh, "SPACE - CHINA", TEAL)
    ey = headline_block(36 + 12, cy, "FIRST PAKISTANI ASTRONAUT "
                        "IN SPACE", 3, INK, bw - 24)
    draw_paragraph(36 + 12, ey + 6,
                   "China's Shenzhou-24 crew took him to the "
                   "Tiangong station today.", 2, INK, bw - 24)
    x2 = 36 + bw + 16
    cy = box(x2, by, bw, bh, "COLOMBIA")
    ey = headline_block(x2 + 12, cy, "GUNMEN HOLD 20 HOSTAGE "
                        "IN CARTAGENA", 3, INK, bw - 24)
    draw_paragraph(x2 + 12, ey + 6,
                   "After a failed armoured-car raid, they seized "
                   "shoppers.", 2, INK, bw - 24)
    x3 = x2 + bw + 16
    cy = box(x3, by, bw, bh, "UNITED STATES")
    ey = headline_block(x3 + 12, cy, "CIA UNCLASSIFIED SYSTEM "
                        "BREACHED", 3, INK, bw - 24)
    draw_paragraph(x3 + 12, ey + 6,
                   "No classified data was compromised, the agency "
                   "says.", 2, INK, bw - 24)

    # ---- numbers strip
    fill_rect(36, 832, W - 72, 3, INK)
    draw_text(36, 844, "THE DAY IN NUMBERS", 2, RED)
    nums = [("11", "HURT IN THE RIYADH STRIKE"),
            ("7,000", "CASUALTIES FROM LANDMINES IN 2026"),
            ("-7%", "NVIDIA SHARES AS HUANG RALLY FADES"),
            ("103.3", "US CONSUMER CONFIDENCE INDEX")]
    col_w = (W - 72) // 4
    for i, (big, small) in enumerate(nums):
        nx = 36 + i * col_w
        draw_text(nx + 6, 864, big, 5, INK)
        draw_paragraph(nx + 6, 906, small, 2, SOFT_INK, col_w - 20)
    fill_rect(36, 946, W - 72, 3, INK)

    # ---- two short boxes (kicker inline, two wrapped lines)
    hw = (W - 72 - 16) // 2
    outline_rect(36, 958, hw, 50, INK, 2)
    draw_paragraph(48, 968,
                   "BANGLADESH: GARMENT WORKERS WIN A 36% PAY RISE "
                   "AFTER PROTESTS", 2, INK, hw - 24)
    x2 = 36 + hw + 16
    outline_rect(x2, 958, hw, 50, INK, 2)
    draw_paragraph(x2 + 12, 968,
                   "AFGHANISTAN: MINES AND OLD ORDNANCE KILLED 257 "
                   "THIS YEAR", 2, INK, hw - 24)

    return bytes(FB)


# ------------------------------------------------------------ PNG out

def png_encode(rgb):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)
        raw += rgb[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png_encode(build()))
    print("wrote", path)


if __name__ == "__main__":
    main()
