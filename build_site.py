#!/usr/bin/env python3
"""Generate cards.js for the cube gallery from pngs/ + cards.yaml.
Run after adding cards or editing cards.yaml:  python build_site.py
(Needs PyYAML:  pip install pyyaml)"""
import os, re, json, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = "pngs"
COLOR_ORDER = ["yellow", "green", "red", "blue", "purple"]

def detect_color(path):
    try:
        from PIL import Image, ImageFile
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        import numpy as np, colorsys
        a = np.array(Image.open(path).convert("RGB")); h, w, _ = a.shape
        reg = a[int(h*0.90):int(h*0.965), int(w*0.30):int(w*0.78)].reshape(-1, 3).astype(float)
        sel = reg[((reg.max(1) - reg.min(1)) > 45) & (reg.max(1) > 70)]
        if len(sel) < 30: return None
        r, g, b = [sel[:, i].mean() for i in range(3)]
        deg = colorsys.rgb_to_hsv(r/255, g/255, b/255)[0] * 360
        if r > 140 and g > 110 and b < 130 and abs(r-g) < 70 and g-b > 25: return "yellow"
        if deg < 22 or deg >= 335: return "red"
        if deg < 70: return "yellow"
        if deg < 175: return "green"
        if deg < 258: return "blue"
        return "purple"
    except Exception:
        return None

def prettify(stem):
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', stem)
    s = re.sub(r'[_-]+', ' ', s).strip()
    return (s[:1].upper() + s[1:]) if s else stem

with open(os.path.join(HERE, "cards.yaml"), encoding="utf-8") as fp:
    meta = (yaml.safe_load(fp) or {}).get("cards", {}) or {}

d = os.path.join(HERE, IMG_DIR)
files = sorted([f for f in os.listdir(d) if f.lower().endswith(".png")],
               key=lambda s: (not s[0].isdigit(), s.lower()))
cards = []
for f in files:
    m = meta.get(f) or {}
    color = m.get("color") or detect_color(os.path.join(d, f)) or "unknown"
    cards.append({"file": f, "name": m.get("name") or prettify(os.path.splitext(f)[0]),
                  "color": color, "level": m.get("level"), "copies": m.get("copies", 1)})

out = ("window.DIR=%s;\nwindow.COLOR_ORDER=%s;\nwindow.CARDS=%s;\n"
       % (json.dumps(IMG_DIR + "/"), json.dumps(COLOR_ORDER), json.dumps(cards, ensure_ascii=False)))
with open(os.path.join(HERE, "cards.js"), "w", encoding="utf-8") as fp:
    fp.write(out)
print("Wrote cards.js with %d cards (from cards.yaml)" % len(cards))
