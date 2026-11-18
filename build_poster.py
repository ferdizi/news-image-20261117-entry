#!/usr/bin/env python3
"""Tuesday 17 November 2026 — one front page, 30 stories, 6 continents.

Draws a 1024x1024 newspaper front page with Pillow, deterministically.
Run:  python3 build_poster.py   # writes entry.png beside this file
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (250, 246, 236)
PAPER = (255, 252, 245)
NAVY = (24, 48, 92)
RED = (176, 58, 46)
GOLD = (178, 140, 40)
INK = (32, 32, 32)
GREY = (110, 105, 95)
BORDER = (205, 195, 175)
SKY = (191, 227, 240)
SAND = (239, 230, 208)
PALE = (232, 238, 225)

REGION = {
    "EUROPE": (31, 78, 121), "MIDDLE EAST": (176, 58, 46),
    "ASIA": (46, 125, 50), "AMERICAS": (125, 60, 152),
    "AFRICA": (20, 143, 119), "GLOBAL": (183, 149, 11),
    "OCEANIA": (202, 111, 30), "UNITED STATES": (31, 78, 121),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
_cache = {}


def font(bold=False, serif=False, size=12):
    key = (bold, serif, size)
    if key not in _cache:
        name = "DejaVuSerif-Bold.ttf" if serif and bold else \
            "DejaVuSerif.ttf" if serif else \
            "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        _cache[key] = ImageFont.truetype(FONT_DIR + name, size)
    return _cache[key]


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_lines(draw, x, y, lines, fnt, fill, lh):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def centre(draw, cx, y, text, fnt, fill):
    draw.text((cx - draw.textlength(text, font=fnt) / 2, y), text,
              font=fnt, fill=fill)


# ---------------------------------------------------------------- data
MAINS = [
    ("EUROPE", "WAR", "UKRAINE BRINGS DOWN A SPAN OF THE KERCH BRIDGE",
     "Road arch drops into the strait in a seven-stage strike, a day after Russia hit Kyiv's bridges."),
    ("MIDDLE EAST", "WAR", "IRAN FIRES DRONES AT A US RADAR IN BAHRAIN",
     "Bahrain says it intercepted the drones; the US then struck a missile site on Qeshm Island."),
    ("ASIA", "DIPLOMACY", "TRUMP LANDS IN MANILA; NEXT, XI AND PUTIN",
     "Quad meets for the first time in two years; Thursday he joins Xi and Putin in Shenzhen \u2014 a first."),
    ("UNITED STATES", "TECH", "NVIDIA POSTS A RECORD $115.8BN QUARTER",
     "Revenue $115.8bn, up 103%; first results since Huang quit. The board will not reinstate him."),
    ("AFRICA", "HEALTH", "EBOLA CASES MORE THAN DOUBLE IN DR CONGO",
     "WHO counts 11,000+ cases and 5,400 deaths in DR Congo; children are a third of the dead."),
    ("ASIA", "POLITICS", "MONGOLIA'S PRESIDENT SAYS HE WILL RESIGN",
     "Khurelsukh denies taking $25m over a railway deal; parliament must accept his resignation."),
    ("GLOBAL", "CLIMATE", "COP31 DRAFT SPLITS THE WORLD ON FOSSIL FUELS",
     "Draft offers 'phase out' or 'transitioning away'; the EU wants the strongest clean-energy signal."),
    ("ASIA", "DEFENCE", "JAPAN SCRAMBLES JETS AT RUSSIAN INCURSION",
     "Two suspected Russian planes enter its airspace for three minutes each; Tokyo protests."),
    ("UNITED STATES", "MARKETS", "DOW SINKS 849 POINTS",
     "Fourth straight fall; the S&P closes at its lowest since July as software stocks slide."),
    ("EUROPE", "RELIGION", "POPE LEO XIV FLIES HOME AFTER 12 DAYS",
     "Lands in Rome at 8:48am after 12 days in Latin America; his lung tumour was 'entirely contained'."),
    ("AMERICAS", "HEALTH", "US LOSES MEASLES-FREE STATUS AFTER 26 YEARS",
     "PAHO ends the US elimination status held since 2000; 5,412 cases in 2026, the most in 35 years."),
    ("OCEANIA", "POLICY", "AUSTRALIA TIGHTENS BACKPACKER VISA RULES",
     "Four months of rural work, up from three, for a second-year visa from March."),
]
ALSO = [
    "Russia says it downed 1,441 drones in two nights",
    "Ukraine: Europeans join peace talks",
    "IMF: Ukraine may get $1.6bn more in aid",
    "Gaza: Berlin urges far more aid",
    "Syria: UN says ~4m have returned home",
    "Jordan and Iraq block Telegram",
    "Pakistan seeks to revive US\u2013Iran talks",
    "Saudis replace Yemen coalition chief",
    "Serbia: students lead new parliament",
    "Poland: Tusk survives confidence vote",
    "COP31: Brazil says draft falls short",
    "WHO: superbugs could kill 39m+ by 2050",
    "Third US carrier arrives in the Gulf",
    "US data centres emit like Denmark",
    "Ecuador fishermen sue US over strike",
    "Mexico: journalist found dead in Acapulco",
    "PNG defends closing Taiwan office",
    "UN rights chief warns over Rwanda hub",
]
MAP_DOTS = [(36.5, 45.3), (50.6, 26.2), (121.0, 14.6), (-121.0, 37.4),
            (23.0, -3.0), (106.9, 47.9), (30.7, 36.9), (130.4, 33.6),
            (-74.0, 40.7), (12.5, 41.9), (-84.4, 33.7), (149.1, -35.3)]
ALSO_DOTS = [(37.6, 55.8), (30.5, 50.4), (-77.0, 38.9), (13.4, 52.5),
             (36.3, 33.5), (35.9, 31.9), (73.1, 33.7), (46.7, 24.7),
             (20.5, 44.8), (21.0, 52.2), (-47.9, -15.8), (6.1, 46.2),
             (51.5, 27.5), (-78.0, 38.5), (-78.5, -0.2), (-99.1, 19.4),
             (147.2, -9.5), (30.1, -1.9)]
ILL_BG = [SKY, SAND, CREAM, PALE, SAND, PALE, SKY, SKY, CREAM, SAND, CREAM, SAND]

# ------------------------------------------------------- illustrations
def ill(draw, n, x0, y0, x1, y1):
    """Flat vector illustration for story n (1-based) in the given box."""
    w, h = x1 - x0, y1 - y0
    X = lambda f: x0 + f * w
    Y = lambda f: y0 + f * h
    draw.rectangle([x0, y0, x1, y1], fill=ILL_BG[n - 1])
    if n == 1:  # Kerch bridge, middle span fallen
        draw.rectangle([x0, Y(0.62), x1, y1], fill=(70, 130, 170))
        draw.rectangle([X(0.02), Y(0.30), X(0.42), Y(0.38)], fill=NAVY)
        draw.rectangle([X(0.58), Y(0.30), X(0.98), Y(0.38)], fill=NAVY)
        draw.rectangle([X(0.06), Y(0.38), X(0.10), Y(0.62)], fill=NAVY)
        draw.rectangle([X(0.88), Y(0.38), X(0.92), Y(0.62)], fill=NAVY)
        draw.polygon([(X(0.44), Y(0.38)), (X(0.56), Y(0.38)),
                      (X(0.52), Y(0.66)), (X(0.46), Y(0.68))], fill=(120, 70, 50))
        draw.arc([X(0.30), Y(0.02), X(0.70), Y(0.55)], 180, 360, fill=NAVY, width=3)
        for cx, cy, r in [(0.50, 0.18, 0.07), (0.56, 0.12, 0.05), (0.45, 0.14, 0.04)]:
            draw.ellipse([X(cx - r), Y(cy - r * w / h), X(cx + r), Y(cy + r * w / h)],
                         fill=(230, 130, 40))
        draw.polygon([(X(0.78), Y(0.10)), (X(0.86), Y(0.13)), (X(0.78), Y(0.16))],
                     fill=INK)
    elif n == 2:  # radar dish + drones over the Gulf
        draw.polygon([(X(0.62), Y(1.0)), (X(1.0), Y(0.55)), (X(1.0), Y(1.0))],
                     fill=(110, 180, 210))
        draw.ellipse([X(0.08), Y(0.12), X(0.38), Y(0.55)], outline=NAVY, width=4)
        draw.line([X(0.23), Y(0.55), X(0.23), Y(0.95)], fill=NAVY, width=4)
        draw.line([X(0.15), Y(0.95), X(0.31), Y(0.95)], fill=NAVY, width=4)
        for cx, cy, r in [(0.52, 0.22, 7), (0.58, 0.30, 5), (0.48, 0.32, 4)]:
            draw.ellipse([X(cx) - r, Y(cy) - r, X(cx) + r, Y(cy) + r], fill=RED)
        for cx, cy in [(0.70, 0.18), (0.82, 0.32), (0.68, 0.45)]:
            draw.polygon([(X(cx), Y(cy - 0.05)), (X(cx + 0.09), Y(cy)),
                          (X(cx), Y(cy + 0.05)), (X(cx - 0.09), Y(cy))], fill=INK)
    elif n == 3:  # three flags + plane, Manila to Shenzhen
        for i, (c1, c2) in enumerate([((200, 40, 40), (255, 255, 255)),
                                      ((200, 40, 40), (255, 220, 0)),
                                      ((255, 255, 255), (40, 80, 180))]):
            fx = 0.10 + i * 0.32
            draw.rectangle([X(fx), Y(0.12), X(fx + 0.22), Y(0.48)], fill=c1, outline=INK)
            draw.rectangle([X(fx), Y(0.30), X(fx + 0.22), Y(0.48)], fill=c2, outline=INK)
            draw.line([X(fx + 0.11), Y(0.12), X(fx + 0.11), Y(0.78)], fill=INK, width=2)
            centre(draw, X(fx + 0.11), Y(0.52), ["US", "CN", "RU"][i],
                   font(bold=True, size=11), INK)
        draw.polygon([(X(0.82), Y(0.18)), (X(0.97), Y(0.24)), (X(0.82), Y(0.30))],
                     fill=INK)
        centre(draw, (x0 + x1) / 2, Y(0.82), "MANILA TO SHENZHEN",
               font(bold=True, size=11), NAVY)
    elif n == 4:  # chip + rising chart
        draw.rectangle([X(0.06), Y(0.20), X(0.38), Y(0.80)], fill=NAVY)
        draw.rectangle([X(0.14), Y(0.35), X(0.30), Y(0.65)], fill=(60, 180, 90))
        for fy in (0.30, 0.50, 0.70):
            draw.line([X(0.02), Y(fy), X(0.06), Y(fy)], fill=NAVY, width=3)
            draw.line([X(0.38), Y(fy), X(0.42), Y(fy)], fill=NAVY, width=3)
        pts = [(X(0.48), Y(0.75)), (X(0.60), Y(0.65)), (X(0.70), Y(0.68)),
               (X(0.82), Y(0.45)), (X(0.94), Y(0.25))]
        draw.line(pts, fill=(40, 160, 60), width=4)
        draw.polygon([(X(0.94), Y(0.25)), (X(0.86), Y(0.25)), (X(0.94), Y(0.38))],
                     fill=(40, 160, 60))
    elif n == 5:  # Ebola virus + big count
        cx, cy, r = X(0.20), Y(0.50), min(w, h) * 0.28
        for a in range(0, 360, 30):
            import math
            dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
            draw.line([cx, cy, cx + dx * r * 1.5, cy + dy * r * 1.5], fill=RED, width=3)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        draw.ellipse([cx - r * 0.4, cy - r * 0.4, cx + r * 0.2, cy + r * 0.2],
                     fill=(255, 120, 100))
        draw.text((X(0.40), Y(0.18)), "11,000+", font=font(bold=True, size=20), fill=RED)
        draw.text((X(0.40), Y(0.58)), "CASES \u00b7 5,400 DEAD",
                  font=font(bold=True, size=9), fill=INK)
    elif n == 6:  # parliament + graft claim
        draw.polygon([(X(0.10), Y(0.42)), (X(0.32), Y(0.12)), (X(0.54), Y(0.42))],
                     fill=NAVY)
        draw.rectangle([X(0.10), Y(0.42), X(0.54), Y(0.85)], fill=(240, 200, 80))
        for fx in (0.16, 0.28, 0.40):
            draw.rectangle([X(fx), Y(0.50), X(fx + 0.05), Y(0.85)], fill=NAVY)
        draw.text((X(0.62), Y(0.15)), "$25M", font=font(bold=True, size=22), fill=RED)
        draw.text((X(0.62), Y(0.55)), "GRAFT CLAIM",
                  font=font(bold=True, size=10), fill=RED)

    elif n == 7:  # globe + thermometer + split arrows
        cx, cy, r = X(0.20), Y(0.50), min(w, h) * 0.30
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 160, 210))
        draw.ellipse([cx - r * 0.5, cy - r * 0.7, cx + r * 0.3, cy - r * 0.1],
                     fill=(60, 170, 80))
        draw.ellipse([cx - r * 0.2, cy + r * 0.2, cx + r * 0.6, cy + r * 0.7],
                     fill=(60, 170, 80))
        draw.rectangle([X(0.48), Y(0.25), X(0.54), Y(0.75)], outline=RED, width=2)
        draw.ellipse([X(0.45), Y(0.68), X(0.57), Y(0.88)], fill=RED)
        draw.line([X(0.66), Y(0.50), X(0.82), Y(0.25)], fill=(40, 160, 60), width=3)
        draw.line([X(0.66), Y(0.50), X(0.82), Y(0.75)], fill=RED, width=3)
        draw.polygon([(X(0.82), Y(0.25)), (X(0.74), Y(0.25)), (X(0.82), Y(0.35))],
                     fill=(40, 160, 60))
    elif n == 8:  # jets + rising sun + radar arcs
        _sx, _sy, _sr = X(0.84), Y(0.50), int(h * 0.38)
        draw.ellipse([_sx - _sr, _sy - _sr, _sx + _sr, _sy + _sr], fill=(200, 50, 50))
        for cx, cy, s in [(0.30, 0.35, 1.0), (0.48, 0.62, 0.8)]:
            draw.polygon([(X(cx), Y(cy - 0.12 * s)), (X(cx + 0.22 * s), Y(cy)),
                          (X(cx), Y(cy + 0.12 * s)), (X(cx - 0.14 * s), Y(cy))],
                         fill=NAVY)
        for r in (0.18, 0.30, 0.42):
            draw.arc([X(0.05 - r), Y(0.5 - r), X(0.05 + r), Y(0.5 + r)],
                     -60, 60, fill=GREY, width=2)
    elif n == 9:  # falling market chart
        for gy in (0.25, 0.50, 0.75):
            draw.line([x0, Y(gy), x1, Y(gy)], fill=(220, 210, 190), width=1)
        pts = [(X(0.05), Y(0.20)), (X(0.25), Y(0.35)), (X(0.45), Y(0.30)),
               (X(0.65), Y(0.60)), (X(0.85), Y(0.70)), (X(0.97), Y(0.88))]
        draw.line(pts, fill=RED, width=4)
        draw.polygon([(X(0.97), Y(0.88)), (X(0.88), Y(0.80)), (X(0.97), Y(0.72))],
                     fill=RED)
    elif n == 10:  # domed church + Vatican flag
        draw.rectangle([X(0.08), Y(0.55), X(0.55), Y(0.90)], fill=(240, 220, 170))
        draw.pieslice([X(0.14), Y(0.18), X(0.49), Y(0.62)], 180, 360, fill=NAVY)
        draw.rectangle([X(0.60), Y(0.25), X(0.78), Y(0.60)], fill=(255, 255, 255),
                       outline=INK)
        draw.rectangle([X(0.60), Y(0.25), X(0.69), Y(0.60)], fill=(250, 210, 60))
        for cx in (0.84, 0.90, 0.96):
            draw.ellipse([X(cx - 0.02), Y(0.75), X(cx + 0.02), Y(0.85)], fill=INK)
    elif n == 11:  # measles virus + shield
        cx, cy, r = X(0.18), Y(0.50), min(w, h) * 0.26
        import math
        for a in range(0, 360, 30):
            dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
            draw.line([cx, cy, cx + dx * r * 1.5, cy + dy * r * 1.5], fill=RED, width=3)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        draw.polygon([(X(0.52), Y(0.10)), (X(0.78), Y(0.10)), (X(0.78), Y(0.48)),
                      (X(0.65), Y(0.72)), (X(0.52), Y(0.48))], fill=NAVY)
        centre(draw, X(0.65), Y(0.24), "26 YRS", font(bold=True, size=12), (255, 255, 255))
        draw.text((X(0.52), Y(0.78)), "5,412 CASES", font=font(bold=True, size=9),
                  fill=RED)
    else:  # 12: backpack + wheat + outback sun
        draw.ellipse([X(0.78), Y(0.10), X(0.98), Y(0.48)], fill=(250, 170, 60))
        draw.rounded_rectangle([X(0.08), Y(0.25), X(0.42), Y(0.90)], radius=12,
                               fill=(180, 90, 40))
        draw.rounded_rectangle([X(0.16), Y(0.12), X(0.34), Y(0.30)], radius=8,
                               outline=(180, 90, 40), width=4)
        for sx in (0.55, 0.65):
            draw.line([X(sx), Y(0.90), X(sx), Y(0.35)], fill=(170, 130, 40), width=3)
            for gy in (0.40, 0.55, 0.70):
                draw.ellipse([X(sx - 0.04), Y(gy), X(sx + 0.04), Y(gy + 0.10)],
                             fill=(220, 180, 60))


# ------------------------------------------------------------- map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-110, 68), (-85, 66), (-65, 60), (-55, 52),
     (-70, 42), (-80, 32), (-90, 21), (-105, 20), (-125, 40), (-155, 58)],
    [(-80, 10), (-60, 0), (-35, -8), (-48, -28), (-65, -45), (-70, -52),
     (-73, -25), (-80, -5)],
    [(-10, 36), (-2, 48), (8, 57), (21, 55), (30, 65), (40, 68), (35, 50),
     (28, 41), (19, 42), (8, 44), (-2, 37)],
    [(-17, 15), (0, 35), (20, 32), (35, 28), (43, 12), (51, 11), (40, -10),
     (30, -30), (15, -28), (9, -5), (-8, 4)],
    [(40, 65), (70, 72), (100, 77), (130, 72), (160, 65), (180, 65),
     (160, 55), (140, 45), (127, 33), (110, 20), (100, 8), (80, 10),
     (70, 22), (55, 28), (45, 35), (38, 45)],
    [(113, -22), (115, -35), (130, -32), (140, -38), (150, -37), (153, -27),
     (142, -11), (126, -14)],
]


def project(lon, lat, mx0, my0, mw, mh):
    x = mx0 + (lon + 180) / 360 * mw
    y = my0 + (85 - lat) / 145 * mh
    return x, y


def draw_map(draw, mx0, my0, mw, mh):
    draw.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=(238, 233, 220),
                   outline=BORDER)
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx0 + 4, my0 + 4, mw - 8, mh - 8)
               for lon, lat in poly]
        draw.polygon(pts, fill=(198, 190, 170), outline=(170, 160, 140))
    for lon, lat in ALSO_DOTS:
        x, y = project(lon, lat, mx0 + 4, my0 + 4, mw - 8, mh - 8)
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(120, 115, 105))
    for i, (lon, lat) in enumerate(MAP_DOTS, 1):
        x, y = project(lon, lat, mx0 + 4, my0 + 4, mw - 8, mh - 8)
        region, _, _, _ = MAINS[i - 1]
        col = REGION[region]
        draw.ellipse([x - 7, y - 7, x + 7, y + 7], fill=col, outline=(255, 255, 255))
        centre(draw, x, y - 5, str(i), font(bold=True, size=8), (255, 255, 255))


# ------------------------------------------------------------- panels
def draw_panel(draw, n, x, y, w, h, lead):
    region, tag, headline, deck = MAINS[n - 1]
    col = REGION[region]
    ill_h = 92 if lead else 46
    draw.rectangle([x, y, x + w, y + h], fill=PAPER, outline=BORDER)
    ill(draw, n, x + 1, y + 1, x + w - 1, y + ill_h)
    draw.line([x, y + ill_h, x + w, y + ill_h], fill=col, width=3)
    bx, by = x + w - 20, y + ill_h
    draw.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=col,
                 outline=(255, 255, 255))
    centre(draw, bx, by - 7, str(n), font(bold=True, size=12), (255, 255, 255))
    ty = y + ill_h + 10
    draw.text((x + 10, ty), f"{region} \u00b7 {tag}",
              font=font(bold=True, size=11), fill=col)
    hs = 19 if lead else 15
    ds = 12 if lead else 11
    hl = wrap(draw, headline, font(bold=True, serif=True, size=hs), w - 20)[:2]
    y2 = text_lines(draw, x + 10, ty + 17, hl,
                    font(bold=True, serif=True, size=hs), INK, hs + 4)
    dl = wrap(draw, deck, font(size=ds), w - 20)[:2]
    text_lines(draw, x + 10, y2 + 3, dl, font(size=ds), (70, 65, 55), ds + 4)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # Masthead
    d.rectangle([0, 0, W, 102], fill=NAVY)
    d.rectangle([0, 102, W, 105], fill=GOLD)
    d.text((16, 10), "THE DAY IN WORLD NEWS", font=font(bold=True, size=15),
           fill=GOLD)
    d.text((16, 32), "Tuesday 17 November 2026",
           font=font(bold=True, serif=True, size=48), fill=(255, 255, 255))
    for txt, fnt, fill, yy in [
            ("30 STORIES", font(bold=True, serif=True, size=28), GOLD, 10),
            ("6 CONTINENTS \u00b7 ONE DAY", font(bold=True, size=14),
             (255, 255, 255), 48)]:
        d.text((W - 16 - d.textlength(txt, font=fnt), yy), txt, font=fnt, fill=fill)
    # Lead row + grid
    xs = [8, 349, 690]
    for i, x in enumerate(xs):
        draw_panel(d, i + 1, x, 108, 326, 194, lead=True)
    n = 4
    for row_y in (308, 452, 596):
        for x in xs:
            draw_panel(d, n, x, row_y, 326, 138, lead=False)
            n += 1
    # Bottom section
    d.text((8, 742), "WHERE IT HAPPENED", font=font(bold=True, size=14), fill=NAVY)
    d.text((452, 742), "ALSO ON TUESDAY 17 NOVEMBER",
           font=font(bold=True, size=14), fill=NAVY)
    d.line([8, 762, 1016, 762], fill=GOLD, width=2)
    draw_map(d, 8, 770, 430, 182)
    legend = [("Europe", REGION["EUROPE"]), ("Middle East", REGION["MIDDLE EAST"]),
              ("Asia", REGION["ASIA"]), ("Americas", REGION["AMERICAS"]),
              ("Africa", REGION["AFRICA"]), ("Oceania", REGION["OCEANIA"])]
    lx = 8
    for name, col in legend:
        d.ellipse([lx, 960, lx + 9, 969], fill=col)
        d.text((lx + 13, 958), name, font=font(size=10), fill=INK)
        lx += 13 + d.textlength(name, font=font(size=10)) + 14
    for i, txt in enumerate(ALSO):
        col_x = 452 if i < 9 else 736
        row_y = 772 + (i % 9) * 20
        d.text((col_x, row_y), f"{i + 13}.", font=font(bold=True, size=11), fill=RED)
        d.text((col_x + 24, row_y), txt, font=font(size=11), fill=INK)
    centre(d, W / 2, 984,
           "Every story here was reported on Tuesday 17 November 2026; "
           "disputed claims are attributed.",
           font(size=11), GREY)
    centre(d, W / 2, 1002,
           "Sources: AP, Reuters, AFP, BBC, Al Jazeera, UN News, WHO. "
           "Original drawings.",
           font(size=11), GREY)
    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
