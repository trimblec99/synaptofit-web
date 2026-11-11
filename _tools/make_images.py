#!/usr/bin/env python3
"""N37b (11 Nov 2026): makes the site's small images from logo-512.png.

Run from anywhere (needs Pillow:  python -m pip install pillow):
    python _tools\\make_images.py

Writes, at the site root:
  logo-52.png     header logo (26 px shown, 2x for sharp screens), aim <= 5 KB
  favicon.ico     browser tab icon, 16 / 32 / 48 px
  share-card.png  1200x630 link-preview image
and re-compresses logo.png + logo-512.png LOSSLESSLY (same pixels, only kept
if the file gets smaller). Safe to run again.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = r"C:\Windows\Fonts"
BG = (10, 10, 10)          # #0A0A0A, the site background
GOLD = (212, 175, 55)      # #D4AF37
INK = (242, 242, 242)      # #f2f2f2
SOFT = (207, 207, 207)     # #cfcfcf


def path(name):
    return os.path.join(ROOT, name)


def kb(name):
    return f"{os.path.getsize(path(name)) / 1024:.1f} KB"


def font(file, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS, file), size)
    except OSError:
        print(f"  (font {file} not found, using Pillow's default)")
        return ImageFont.load_default(size)


src = Image.open(path("logo-512.png")).convert("RGBA")

# 1. Header logo, 52 px. Quantised to a palette only if the plain version is
#    over the 5 KB budget (palette keeps transparency; tiny loss at 52 px).
small = src.resize((52, 52), Image.LANCZOS)
small.save(path("logo-52.png"), optimize=True)
if os.path.getsize(path("logo-52.png")) > 5 * 1024:
    small.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(
        path("logo-52.png"), optimize=True)
print("wrote logo-52.png", kb("logo-52.png"))

# 2. Favicon.
src.save(path("favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
print("wrote favicon.ico", kb("favicon.ico"))

# 3. Share card, 1200 x 630: logo left, name + line right, site address below.
W, H = 1200, 630
card = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(card)
draw.rectangle([0, H - 8, W, H], fill=GOLD)              # thin gold base line

logo_size = 340
logo = src.resize((logo_size, logo_size), Image.LANCZOS)
lx, ly = 100, (H - logo_size) // 2 - 10
card.paste(logo, (lx, ly), logo)

x = lx + logo_size + 70
name_font = font("segoeuib.ttf", 92)
line_font = font("segoeui.ttf", 40)
url_font = font("segoeuisl.ttf", 30)

y = 175
draw.text((x, y), "Synapto", font=name_font, fill=INK)
draw.text((x + draw.textlength("Synapto", font=name_font), y), "Fit",
          font=name_font, fill=GOLD)

# The line, wrapped to the space on the right.
max_w = W - x - 70
words, lines, cur = "The fitness tracker that works without signal.".split(), [], ""
for w in words:
    test = (cur + " " + w).strip()
    if draw.textlength(test, font=line_font) <= max_w:
        cur = test
    else:
        lines.append(cur)
        cur = w
lines.append(cur)
y += 130
for ln in lines:
    draw.text((x, y), ln, font=line_font, fill=SOFT)
    y += 54
draw.text((x, y + 26), "synaptofit.com", font=url_font, fill=GOLD)

card.save(path("share-card.png"), optimize=True)
print("wrote share-card.png", kb("share-card.png"))

# 4. Lossless re-compression of the existing logos (kept only if smaller).
for name in ("logo.png", "logo-512.png"):
    before = os.path.getsize(path(name))
    tmp = path(name + ".tmp.png")
    Image.open(path(name)).save(tmp, optimize=True)
    if os.path.getsize(tmp) < before:
        os.replace(tmp, path(name))
        print(f"recompressed {name}: {before / 1024:.1f} KB -> {kb(name)}")
    else:
        os.remove(tmp)
        print(f"{name}: already as small as it gets ({before / 1024:.1f} KB)")
