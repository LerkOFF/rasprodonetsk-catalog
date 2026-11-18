"""Иконки приложения (PWA) для site/icons. Запуск: python3 make_icons.py"""
import os
from PIL import Image, ImageDraw

os.makedirs("site/icons", exist_ok=True)

def icon(size, maskable=False):
    s = size * 4                              # рисуем крупнее и сжимаем, чтобы края были гладкие
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bg = (217, 72, 43, 255)
    if maskable:
        d.rectangle([0, 0, s, s], fill=bg)    # maskable: фон до краёв, символ внутри безопасной зоны
        k = 0.62
    else:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=bg)
        k = 0.7
    c = s / 2
    w = s * k / 2
    # ценник: скруглённый прямоугольник с «ушком» и отверстием
    body = [c - w * 0.78, c - w * 0.62, c + w * 0.78, c + w * 0.62]
    d.rounded_rectangle(body, radius=int(w * 0.22), fill=(255, 255, 255, 255))
    hole_r = w * 0.13
    d.ellipse([c - hole_r, body[1] + w * 0.16 - hole_r, c + hole_r, body[1] + w * 0.16 + hole_r], fill=bg)
    # знак процента
    r = w * 0.17
    d.ellipse([c - w * 0.40 - r, c + w * 0.02 - r, c - w * 0.40 + r, c + w * 0.02 + r], outline=bg, width=int(s * 0.022))
    d.ellipse([c + w * 0.40 - r, c + w * 0.40 - r, c + w * 0.40 + r, c + w * 0.40 + r], outline=bg, width=int(s * 0.022))
    d.line([c + w * 0.38, c - w * 0.18, c - w * 0.38, c + w * 0.5], fill=bg, width=int(s * 0.03))
    return im.resize((size, size), Image.LANCZOS)

icon(192).save("site/icons/icon-192.png")
icon(512).save("site/icons/icon-512.png")
icon(512, True).save("site/icons/maskable-512.png")
icon(180).convert("RGB").save("site/icons/apple-touch-icon.png")   # iOS не любит прозрачность
