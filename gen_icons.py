# -*- coding: utf-8 -*-
"""Generate PWA icons: gradient rounded square with a white Chinese char."""
from PIL import Image, ImageDraw, ImageFont
import os

SIZE = 512
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

# diagonal gradient background (full-bleed square, safe for maskable)
c1 = (16, 26, 74)    # deep indigo
c2 = (74, 42, 126)   # purple
c3 = (139, 106, 220) # light violet glow
px = img.load()
for y in range(SIZE):
    for x in range(SIZE):
        t = (x + y) / (2 * SIZE)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        # top-left radial glow
        dx, dy = x - SIZE * 0.28, y - SIZE * 0.22
        d = (dx * dx + dy * dy) / (SIZE * SIZE * 0.55)
        glow = max(0.0, 1.0 - d) * 0.55
        r = min(255, int(r + (c3[0] - r) * glow))
        g = min(255, int(g + (c3[1] - g) * glow))
        b = min(255, int(b + (c3[2] - b) * glow))
        px[x, y] = (r, g, b, 255)

# rounded-corner mask (radius ~22% of side)
mask = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=int(SIZE * 0.225), fill=255)
img.putalpha(mask)

draw = ImageDraw.Draw(img)

# pick a CJK font
font_path = None
for p in (r"C:\Windows\Fonts\simkai.ttf",
          r"C:\Windows\Fonts\STKAITI.TTF",
          r"C:\Windows\Fonts\msyhbd.ttc",
          r"C:\Windows\Fonts\msyh.ttc"):
    if os.path.exists(p):
        font_path = p
        break
assert font_path, "no CJK font found"
font = ImageFont.truetype(font_path, 268)

ch = "研"
# soft shadow
shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
ImageDraw.Draw(shadow).text((SIZE / 2 + 5, SIZE / 2 + 12), ch, font=font, fill=(0, 0, 0, 110))
shadow = shadow.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(10))
img.alpha_composite(shadow)
draw.text((SIZE / 2, SIZE / 2 - 6), ch, font=font, fill=(255, 255, 255, 255), anchor="mm")

# small sparkle top-right
sx, sy, sr = 392, 118, 26
star = [(sx, sy - sr), (sx + sr * 0.28, sy - sr * 0.28), (sx + sr, sy),
        (sx + sr * 0.28, sy + sr * 0.28), (sx, sy + sr), (sx - sr * 0.28, sy + sr * 0.28),
        (sx - sr, sy), (sx - sr * 0.28, sy - sr * 0.28)]
draw.polygon(star, fill=(255, 255, 255, 235))

out = r"D:\NaoZhong\kaoyan-countdown"
img.save(os.path.join(out, "icon-512.png"))
img.resize((192, 192), Image.LANCZOS).save(os.path.join(out, "icon-192.png"))
img.resize((180, 180), Image.LANCZOS).save(os.path.join(out, "apple-touch-icon.png"))
print("icons written ->", out, "font:", os.path.basename(font_path))
