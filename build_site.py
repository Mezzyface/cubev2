#!/usr/bin/env python3
"""Generate cards.js (card data) for the cube gallery from the pngs/ folder.
Re-run after adding cards:  python build_site.py

The page itself is index.html + style.css + app.js (static). This script only
rewrites cards.js. Color/level per card live in CARD_META (keyed by filename);
color is auto-detected from the image for any card not listed."""
import os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = "pngs"
COLOR_ORDER = ["yellow", "green", "red", "blue", "purple"]

NAME_OVERRIDES = {
    "alient": "aliEn T", "Barbara": "Barbra", "ballonparty": "Balloon Party",
    "buddyfairchild": "Buddy Fairchild", "dancewithme": "Dance with me",
    "festivaltime": "Festival Time", "peptalk": "Pep Talk", "piday": "Pi Day",
    "puppetshow": "Puppet Show", "johnTitor": "John Titor", "laSource": "La Source",
    "toothFairy": "Tooth Fairy", "RayGun": "Ray Gun", "RedEnvelopes": "Red Envelopes",
    "SkyLantern": "Sky Lantern", "MealTime": "Meal Time", "BunnyBunny": "Bunny Bunny",
    "DumplingPlatter": "Dumpling Platter",
}

CARD_META = {
    "37.png": ("blue", 0), "Barbara.png": ("blue", 3), "Blonney.png": ("blue", 1),
    "BunnyBunny.png": ("yellow", 3), "DumplingPlatter.png": ("yellow", 2),
    "Matilda.png": ("blue", 0), "MealTime.png": ("yellow", 2), "Mondlicht.png": ("red", 1),
    "RayGun.png": ("yellow", 3), "RedEnvelopes.png": ("yellow", 1), "SkyLantern.png": ("yellow", 1),
    "TTT.png": ("blue", 0), "alient.png": ("yellow", 1), "apple.png": ("blue", 0),
    "ballonparty.png": ("blue", 0), "buddyfairchild.png": ("blue", 1), "cake.png": ("blue", 1),
    "dancewithme.png": ("green", 1), "festivaltime.png": ("blue", 2), "johnTitor.png": ("blue", 2),
    "laSource.png": ("blue", 3), "mine.png": ("red", 1), "peptalk.png": ("red", 3),
    "pickles.png": ("blue", 0), "piday.png": ("blue", 1), "puppetshow.png": ("green", 3),
    "satsuki.png": ("blue", 1), "sotheby.png": ("red", 3), "spathodea.png": ("blue", 3),
    "toothFairy.png": ("blue", 2), "x.png": ("blue", 2),
    "cristallo.png": ("green", 1), "onion.png": ("green", 3),
}

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
    if stem in NAME_OVERRIDES: return NAME_OVERRIDES[stem]
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', stem)
    s = re.sub(r'[_-]+', ' ', s).strip()
    return (s[:1].upper() + s[1:]) if s else stem

d = os.path.join(HERE, IMG_DIR)
files = sorted([f for f in os.listdir(d) if f.lower().endswith(".png")],
               key=lambda s: (not s[0].isdigit(), s.lower()))
cards = []
for f in files:
    meta = CARD_META.get(f)
    color = meta[0] if meta else (detect_color(os.path.join(d, f)) or "unknown")
    level = meta[1] if meta else None
    cards.append({"file": f, "name": prettify(os.path.splitext(f)[0]),
                  "color": color, "level": level})

out = ("window.DIR=%s;\nwindow.COLOR_ORDER=%s;\nwindow.CARDS=%s;\n"
       % (json.dumps(IMG_DIR + "/"), json.dumps(COLOR_ORDER),
          json.dumps(cards, ensure_ascii=False)))
with open(os.path.join(HERE, "cards.js"), "w", encoding="utf-8") as fp:
    fp.write(out)
print("Wrote cards.js with %d cards" % len(cards))
