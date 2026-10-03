#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор иконки NewVisuals Launcher: icon.png + launcher.ico."""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SIZE = 256
FONT_PATH = r"C:\Windows\Fonts\segoeuib.ttf"


def rounded_mask(size, box, radius):
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=radius, fill=255)
    return mask


def main():
    box = [10, 10, SIZE - 10, SIZE - 10]
    mask = rounded_mask(SIZE, box, 58)
    transparent = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

    # фон-градиент
    bg = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))
    bd = ImageDraw.Draw(bg)
    for i in range(SIZE):
        t = i / SIZE
        bd.line([(0, i), (SIZE, i)],
                fill=(int(24 + (12 - 24) * t), int(24 + (12 - 24) * t),
                      int(48 + (24 - 48) * t), 255))
    img = Image.composite(bg, transparent, mask)

    # два пересекающихся круга
    circles = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cd = ImageDraw.Draw(circles)
    cd.ellipse([36, 68, 170, 202], fill=(77, 155, 255, 215))
    cd.ellipse([94, 98, 228, 232], fill=(155, 107, 255, 215))
    circles = Image.composite(circles, transparent, mask)
    img = Image.alpha_composite(img, circles)

    # глянец сверху
    gloss = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    for i in range(96):
        a = int(60 * (1 - i / 96))
        gd.line([(34, 28 + i), (SIZE - 34, 28 + i)], fill=(255, 255, 255, a))
    gloss = Image.composite(gloss, transparent, mask)
    img = Image.alpha_composite(img, gloss)

    # рамка и надпись
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=58, outline=(74, 74, 116, 255), width=4)
    d.rounded_rectangle([15, 15, SIZE - 15, SIZE - 15], radius=53,
                        outline=(120, 180, 255, 255), width=2)

    font = ImageFont.truetype(FONT_PATH, 104)
    text = "NV"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx, ty = (SIZE - tw) / 2 - bbox[0], (SIZE - th) / 2 - bbox[1] - 4
    d.text((tx + 4, ty + 5), text, font=font, fill=(5, 5, 12, 230))
    d.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))

    img.save(os.path.join(ROOT_DIR, "icon.png"))
    img.save(os.path.join(ROOT_DIR, "launcher.ico"),
             sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("icon.png + launcher.ico готовы")


if __name__ == "__main__":
    main()
