#!/usr/bin/env python3
"""Tuesday 17 November 2026 — one front page, 30 stories, 6 continents.

Draws a 1024x1024 newspaper front page with Pillow. Deterministic:
same input always writes the same bytes. Run: python3 build_poster.py
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (250, 246, 236)
NAVY = (24, 48, 92)
RED = (176, 58, 46)
GOLD = (178, 140, 40)
INK = (30, 30, 30)
MUTED = (107, 101, 88)
PANEL_LINE = (210, 203, 188)
MAP_FILL = (207, 199, 180)
MAP_EDGE = (168, 159, 136)

REGION_COLOUR = {
    "EUROPE": (31, 78, 121),
    "MIDDLE EAST": (176, 58, 46),
    "ASIA": (46, 125, 50),
    "UNITED STATES": (31, 78, 121),
    "AMERICAS": (125, 60, 152),
    "AFRICA": (20, 143, 119),
    "GLOBAL": (183, 149, 11),
    "OCEANIA": (202, 111, 30),
}

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- data
# (n, region, tag, headline, deck, lon, lat)
MAINS = [
    (1, "EUROPE", "WAR",
     "UKRAINE BRINGS DOWN A SPAN OF THE KERCH BRIDGE",
     "Road arch drops into the strait in a seven-stage strike, a day after Russia hit Kyiv's bridges.",
     36.5, 45.3),
    (2, "MIDDLE EAST", "WAR",
     "IRAN FIRES DRONES AT A US RADAR IN BAHRAIN",
     "Bahrain says it intercepted the drones; the US then struck a missile site on Qeshm Island.",
     50.6, 26.2),
    (3, "ASIA", "DIPLOMACY",
     "TRUMP LANDS IN MANILA; NEXT, XI AND PUTIN",
     "Quad meets for the first time in two years; Thursday he joins Xi and Putin in Shenzhen \u2014 a first.",
     121.0, 14.6),
    (4, "UNITED STATES", "TECH",
     "NVIDIA POSTS A RECORD $115.8BN QUARTER",
     "Revenue $115.8bn, up 103%; first results since Huang quit. The board will not reinstate him.",
     -121.0, 37.4),
    (5, "AFRICA", "HEALTH",
     "EBOLA CASES MORE THAN DOUBLE IN DR CONGO",
     "WHO counts 11,000+ cases and 5,400 deaths in DR Congo; children are a third of the dead.",
     23.0, -3.0),
    (6, "ASIA", "POLITICS",
     "MONGOLIA'S PRESIDENT SAYS HE WILL RESIGN",
     "Khurelsukh denies taking $25m over a railway deal; parliament must accept his resignation.",
     106.9, 47.9),
    (7, "GLOBAL", "CLIMATE",
     "COP31 DRAFT SPLITS THE WORLD ON FOSSIL FUELS",
     "Draft offers 'phase out' or 'transitioning away'; the EU wants the strongest clean-energy signal.",
     30.7, 36.9),
    (8, "ASIA", "DEFENCE",
     "JAPAN SCRAMBLES JETS AT RUSSIAN INCURSION",
     "Two suspected Russian planes enter its airspace for three minutes each; Tokyo protests.",
     130.4, 33.6),
    (9, "UNITED STATES", "MARKETS",
     "DOW SINKS 849 POINTS",
     "Fourth straight fall; the S&P closes at its lowest since July as software stocks slide.",
     -74.0, 40.7),
    (10, "EUROPE", "RELIGION",
     "POPE LEO XIV FLIES HOME AFTER 12 DAYS",
     "Lands in Rome at 8:48am after 12 days in Latin America; his lung tumour was 'entirely contained'.",
     12.5, 41.9),
    (11, "AMERICAS", "HEALTH",
     "US LOSES MEASLES-FREE STATUS AFTER 26 YEARS",
     "PAHO ends the US elimination status held since 2000; 5,412 cases in 2026, the most in 35 years.",
     -84.4, 33.7),
    (12, "OCEANIA", "POLICY",
     "AUSTRALIA TIGHTENS BACKPACKER VISA RULES",
     "Four months of rural work, up from three, for a second-year visa from March.",
     149.1, -35.3),
]

# (n, one-liner, lon, lat)
ALSO = [
    (13, "Russia says it downed 1,441 drones in two nights", 37.6, 55.8),
    (14, "Ukraine: Europeans join peace talks", 30.5, 50.4),
    (15, "IMF: Ukraine may get $1.6bn more in aid", -77.0, 38.9),
    (16, "Gaza: Berlin urges far more aid", 13.4, 52.5),
    (17, "Syria: UN says ~4m have returned home", 36.3, 33.5),
    (18, "Jordan and Iraq block Telegram", 35.9, 31.9),
    (19, "Pakistan seeks to revive US\u2013Iran talks", 73.1, 33.7),
    (20, "Saudis replace Yemen coalition chief", 46.7, 24.7),
    (21, "Serbia: students lead new parliament", 20.5, 44.8),
    (22, "Poland: Tusk survives confidence vote", 21.0, 52.2),
    (23, "COP31: Brazil says draft falls short", -47.9, -15.8),
    (24, "WHO: superbugs could kill 39m+ by 2050", 6.1, 46.2),
    (25, "Third US carrier arrives in the Gulf", 51.5, 27.5),
    (26, "US data centres emit like Denmark", -78.0, 38.5),
    (27, "Ecuador fishermen sue US over strike", -78.5, -0.2),
    (28, "Mexico: journalist found dead in Acapulco", -99.1, 19.4),
    (29, "PNG defends closing Taiwan office", 147.2, -9.5),
    (30, "UN rights chief warns over Rwanda hub", 30.1, -1.9),
]

LEGEND = [("Europe", (31, 78, 121)), ("Middle East", (176, 58, 46)),
          ("Asia", (46, 125, 50)), ("Americas", (125, 60, 152)),
          ("Africa", (20, 143, 119)), ("Oceania", (202, 111, 30))]


# ---------------------------------------------------------------- helpers
def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines fitting max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def balance_two(draw, text, fnt, max_w):
    """Split words into the two most even lines that both fit max_w.

    Greedy wrapping wastes width on line 1 and strands one word on
    line 3; balancing keeps the whole headline on two lines.
    Returns None when no two-line split fits.
    """
    words = text.split()
    best = None
    for k in range(1, len(words)):
        l1, l2 = " ".join(words[:k]), " ".join(words[k:])
        w1 = draw.textlength(l1, font=fnt)
        w2 = draw.textlength(l2, font=fnt)
        if w1 <= max_w and w2 <= max_w:
            score = max(w1, w2)
            if best is None or score < best[0]:
                best = (score, [l1, l2])
    if best is not None:
        return best[1]
    return None


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap and cap to max_lines, adding an ellipsis when clipped."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    while out and draw.textlength(out[-1] + "\u2026", font=fnt) > max_w:
        out[-1] = out[-1][:-1]
    out[-1] = out[-1] + "\u2026"
    return out


def text_block(draw, x, y, lines, fnt, fill, leading):
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


def badge(draw, cx, cy, n, colour, r=11):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour,
                 outline=(255, 255, 255), width=2)
    fnt = font(SANS_B, 11 if n < 10 else 10)
    tw = draw.textlength(str(n), font=fnt)
    th = fnt.getbbox(str(n))[3] - fnt.getbbox(str(n))[1]
    draw.text((cx - tw / 2, cy - th / 2 - 1), str(n), font=fnt,
              fill=(255, 255, 255))


def sky(draw, x, y, w, h, top, bottom):
    """Vertical two-stop sky gradient, drawn as horizontal bands."""
    for row in range(h):
        t = row / max(h - 1, 1)
        col = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(x, y + row), (x + w, y + row)], fill=col)


# ------------------------------------------------------- illustrations
# Each painter gets the art box (x, y, w, h). Flat vector shapes only;
# the only lettering inside an art box is the caption the spec calls
# for (panel 3, 5, 6, 11). Everything else is drawn, never written.
def paint(draw, n, x, y, w, h):
    if n == 1:
        sky(draw, x, y, w, h, (198, 228, 240), (170, 205, 225))
        draw.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(72, 128, 168))
        draw.rectangle([x, y + int(h * 0.30), x + int(w * 0.42), y + int(h * 0.38)], fill=NAVY)
        draw.rectangle([x + int(w * 0.58), y + int(h * 0.30), x + w, y + int(h * 0.38)], fill=NAVY)
        draw.rectangle([x + int(w * 0.06), y + int(h * 0.38), x + int(w * 0.10), y + int(h * 0.62)], fill=NAVY)
        draw.rectangle([x + int(w * 0.88), y + int(h * 0.38), x + int(w * 0.92), y + int(h * 0.62)], fill=NAVY)
        draw.polygon([(x + int(w * 0.44), y + int(h * 0.38)),
                      (x + int(w * 0.56), y + int(h * 0.38)),
                      (x + int(w * 0.52), y + int(h * 0.66)),
                      (x + int(w * 0.46), y + int(h * 0.68))], fill=(122, 72, 52))
        draw.arc([x + int(w * 0.30), y, x + int(w * 0.70), y + int(h * 0.55)],
                 180, 360, fill=NAVY, width=3)
        for cx, cy, r in [(0.50, 0.16, 0.05), (0.57, 0.10, 0.035), (0.44, 0.12, 0.03)]:
            rx, ry = int(w * r), int(w * r)
            draw.ellipse([x + int(w * cx) - rx, y + int(h * cy) - ry,
                          x + int(w * cx) + rx, y + int(h * cy) + ry], fill=(232, 132, 42))
        draw.polygon([(x + int(w * 0.78), y + int(h * 0.10)),
                      (x + int(w * 0.86), y + int(h * 0.13)),
                      (x + int(w * 0.78), y + int(h * 0.16))], fill=INK)
    elif n == 2:
        draw.rectangle([x, y, x + w, y + h], fill=(238, 230, 208))
        draw.polygon([(x + int(w * 0.62), y + h), (x + w, y + int(h * 0.55)),
                      (x + w, y + h)], fill=(112, 182, 212))
        draw.ellipse([x + int(w * 0.08), y + int(h * 0.10),
                      x + int(w * 0.38), y + int(h * 0.52)], outline=NAVY, width=4)
        draw.line([x + int(w * 0.23), y + int(h * 0.52), x + int(w * 0.23), y + h - 4],
                  fill=NAVY, width=4)
        draw.line([x + int(w * 0.15), y + h - 4, x + int(w * 0.31), y + h - 4],
                  fill=NAVY, width=4)
        for cx, cy, r in [(0.52, 0.20, 6), (0.58, 0.28, 5), (0.48, 0.30, 4)]:
            draw.ellipse([x + int(w * cx) - r, y + int(h * cy) - r,
                          x + int(w * cx) + r, y + int(h * cy) + r], fill=RED)
        for cx, cy in [(0.70, 0.16), (0.82, 0.30), (0.68, 0.43)]:
            draw.polygon([(x + int(w * cx), y + int(h * (cy - 0.05))),
                          (x + int(w * (cx + 0.09)), y + int(h * cy)),
                          (x + int(w * cx), y + int(h * (cy + 0.05))),
                          (x + int(w * (cx - 0.09)), y + int(h * cy))], fill=INK)
    elif n == 3:
        draw.rectangle([x, y, x + w, y + h], fill=(250, 246, 236))
        labels = ["US", "CN", "RU"]
        tops = [((200, 40, 40), (255, 255, 255)), ((200, 40, 40), (255, 220, 0)),
                ((255, 255, 255), (40, 80, 180))]
        for i, (c1, c2) in enumerate(tops):
            fx = 0.10 + i * 0.32
            draw.rectangle([x + int(w * fx), y + int(h * 0.10),
                            x + int(w * (fx + 0.22)), y + int(h * 0.44)],
                           fill=c1, outline=INK)
            draw.rectangle([x + int(w * fx), y + int(h * 0.27),
                            x + int(w * (fx + 0.22)), y + int(h * 0.44)],
                           fill=c2, outline=INK)
            draw.line([x + int(w * (fx + 0.11)), y + int(h * 0.10),
                       x + int(w * (fx + 0.11)), y + int(h * 0.72)], fill=INK, width=2)
            lab = font(SANS_B, 11)
            tw = draw.textlength(labels[i], font=lab)
            draw.text((x + int(w * (fx + 0.11)) - tw / 2, y + int(h * 0.50)),
                      labels[i], font=lab, fill=INK)
        draw.polygon([(x + int(w * 0.82), y + int(h * 0.16)),
                      (x + int(w * 0.97), y + int(h * 0.22)),
                      (x + int(w * 0.82), y + int(h * 0.28))], fill=INK)
        cap = font(SANS_B, 11)
        tw = draw.textlength("MANILA TO SHENZHEN", font=cap)
        draw.text((x + (w - tw) / 2, y + int(h * 0.78)), "MANILA TO SHENZHEN",
                  font=cap, fill=NAVY)
    elif n == 4:
        draw.rectangle([x, y, x + w, y + h], fill=(232, 238, 225))
        draw.rectangle([x + int(w * 0.06), y + int(h * 0.18),
                        x + int(w * 0.38), y + int(h * 0.82)], fill=NAVY)
        draw.rectangle([x + int(w * 0.14), y + int(h * 0.33),
                        x + int(w * 0.30), y + int(h * 0.67)], fill=(62, 182, 92))
        for fy in (0.28, 0.50, 0.72):
            draw.line([x + int(w * 0.02), y + int(h * fy), x + int(w * 0.06), y + int(h * fy)],
                      fill=NAVY, width=3)
            draw.line([x + int(w * 0.38), y + int(h * fy), x + int(w * 0.42), y + int(h * fy)],
                      fill=NAVY, width=3)
        pts = [(x + int(w * 0.48), y + int(h * 0.78)), (x + int(w * 0.60), y + int(h * 0.66)),
               (x + int(w * 0.70), y + int(h * 0.70)), (x + int(w * 0.82), y + int(h * 0.46)),
               (x + int(w * 0.94), y + int(h * 0.24))]
        draw.line(pts, fill=(42, 162, 62), width=4)
        draw.polygon([(x + int(w * 0.94), y + int(h * 0.24)),
                      (x + int(w * 0.86), y + int(h * 0.24)),
                      (x + int(w * 0.94), y + int(h * 0.38))], fill=(42, 162, 62))
    elif n == 5:
        draw.rectangle([x, y, x + w, y + h], fill=(238, 230, 208))
        cx, cy = x + int(w * 0.20), y + int(h * 0.50)
        r = int(min(w, h) * 0.26)
        for a in range(0, 360, 30):
            dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
            draw.line([cx, cy, cx + dx * r * 1.5, cy + dy * r * 1.5], fill=RED, width=3)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        draw.ellipse([cx - int(r * 0.4), cy - int(r * 0.4),
                      cx + int(r * 0.2), cy + int(r * 0.2)], fill=(255, 122, 102))
        big = font(SANS_B, 20 if h > 60 else 14)
        draw.text((x + int(w * 0.40), y + int(h * 0.16)), "11,000+", font=big, fill=RED)
        small = font(SANS_B, 9)
        draw.text((x + int(w * 0.40), y + int(h * 0.60)), "CASES \u00b7 5,400 DEAD",
                  font=small, fill=INK)
    elif n == 6:
        draw.rectangle([x, y, x + w, y + h], fill=(232, 238, 225))
        draw.polygon([(x + int(w * 0.10), y + int(h * 0.42)),
                      (x + int(w * 0.32), y + int(h * 0.10)),
                      (x + int(w * 0.54), y + int(h * 0.42))], fill=NAVY)
        draw.rectangle([x + int(w * 0.10), y + int(h * 0.42),
                        x + int(w * 0.54), y + int(h * 0.88)], fill=(240, 202, 82))
        for fx in (0.16, 0.28, 0.40):
            draw.rectangle([x + int(w * fx), y + int(h * 0.50),
                            x + int(w * (fx + 0.05)), y + int(h * 0.88)], fill=NAVY)
        draw.text((x + int(w * 0.62), y + int(h * 0.12)), "$25M",
                  font=font(SANS_B, 22 if h > 60 else 15), fill=RED)
        draw.text((x + int(w * 0.62), y + int(h * 0.55)), "GRAFT CLAIM",
                  font=font(SANS_B, 10), fill=RED)
    elif n == 7:
        sky(draw, x, y, w, h, (198, 228, 240), (220, 235, 225))
        cx, cy = x + int(w * 0.20), y + int(h * 0.50)
        r = int(min(w, h) * 0.28)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(92, 162, 212))
        draw.ellipse([cx - int(r * 0.5), cy - int(r * 0.7),
                      cx + int(r * 0.3), cy - int(r * 0.1)], fill=(62, 172, 82))
        draw.ellipse([cx - int(r * 0.2), cy + int(r * 0.2),
                      cx + int(r * 0.6), cy + int(r * 0.7)], fill=(62, 172, 82))
        draw.rectangle([x + int(w * 0.48), y + int(h * 0.22),
                        x + int(w * 0.54), y + int(h * 0.78)], outline=RED, width=2)
        draw.ellipse([x + int(w * 0.45), y + int(h * 0.68),
                      x + int(w * 0.57), y + int(h * 0.90)], fill=RED)
        draw.line([x + int(w * 0.66), y + int(h * 0.50), x + int(w * 0.82), y + int(h * 0.24)],
                  fill=(42, 162, 62), width=3)
        draw.line([x + int(w * 0.66), y + int(h * 0.50), x + int(w * 0.82), y + int(h * 0.76)],
                  fill=RED, width=3)
        draw.polygon([(x + int(w * 0.82), y + int(h * 0.24)),
                      (x + int(w * 0.74), y + int(h * 0.24)),
                      (x + int(w * 0.82), y + int(h * 0.36))], fill=(42, 162, 62))
    elif n == 8:
        sky(draw, x, y, w, h, (198, 228, 240), (190, 215, 235))
        sx, sy, sr = x + int(w * 0.84), y + int(h * 0.50), int(h * 0.36)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(202, 52, 52))
        for cx, cy, s in [(0.30, 0.35, 1.0), (0.48, 0.62, 0.8)]:
            draw.polygon([(x + int(w * cx), y + int(h * (cy - 0.12 * s))),
                          (x + int(w * (cx + 0.22 * s)), y + int(h * cy)),
                          (x + int(w * cx), y + int(h * (cy + 0.12 * s))),
                          (x + int(w * (cx - 0.14 * s)), y + int(h * cy))], fill=NAVY)
        for rr in (0.18, 0.30, 0.42):
            draw.arc([x + int(w * (0.05 - rr)), y + int(h * (0.5 - rr)),
                      x + int(w * (0.05 + rr)), y + int(h * (0.5 + rr))],
                     -60, 60, fill=MUTED, width=2)
    elif n == 9:
        draw.rectangle([x, y, x + w, y + h], fill=(250, 246, 236))
        for gy in (0.25, 0.50, 0.75):
            draw.line([x, y + int(h * gy), x + w, y + int(h * gy)],
                      fill=(222, 212, 192), width=1)
        pts = [(x + int(w * 0.05), y + int(h * 0.20)), (x + int(w * 0.25), y + int(h * 0.35)),
               (x + int(w * 0.45), y + int(h * 0.30)), (x + int(w * 0.65), y + int(h * 0.60)),
               (x + int(w * 0.85), y + int(h * 0.70)), (x + int(w * 0.97), y + int(h * 0.88))]
        draw.line(pts, fill=RED, width=4)
        draw.polygon([(x + int(w * 0.97), y + int(h * 0.88)),
                      (x + int(w * 0.88), y + int(h * 0.80)),
                      (x + int(w * 0.97), y + int(h * 0.72))], fill=RED)
    elif n == 10:
        draw.rectangle([x, y, x + w, y + h], fill=(238, 230, 208))
        draw.rectangle([x + int(w * 0.08), y + int(h * 0.55),
                        x + int(w * 0.55), y + int(h * 0.92)], fill=(240, 222, 172))
        draw.pieslice([x + int(w * 0.14), y + int(h * 0.16),
                       x + int(w * 0.49), y + int(h * 0.62)], 180, 360, fill=NAVY)
        draw.rectangle([x + int(w * 0.60), y + int(h * 0.24),
                        x + int(w * 0.78), y + int(h * 0.62)], fill=(255, 255, 255), outline=INK)
        draw.rectangle([x + int(w * 0.60), y + int(h * 0.24),
                        x + int(w * 0.69), y + int(h * 0.62)], fill=(250, 212, 62))
        for cx in (0.84, 0.90, 0.96):
            draw.ellipse([x + int(w * (cx - 0.02)), y + int(h * 0.74),
                          x + int(w * (cx + 0.02)), y + int(h * 0.86)], fill=INK)
    elif n == 11:
        draw.rectangle([x, y, x + w, y + h], fill=(250, 246, 236))
        cx, cy = x + int(w * 0.18), y + int(h * 0.50)
        r = int(min(w, h) * 0.24)
        for a in range(0, 360, 30):
            dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
            draw.line([cx, cy, cx + dx * r * 1.5, cy + dy * r * 1.5], fill=RED, width=3)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        draw.polygon([(x + int(w * 0.52), y + int(h * 0.08)),
                      (x + int(w * 0.78), y + int(h * 0.08)),
                      (x + int(w * 0.78), y + int(h * 0.48)),
                      (x + int(w * 0.65), y + int(h * 0.72)),
                      (x + int(w * 0.52), y + int(h * 0.48))], fill=NAVY)
        lab = font(SANS_B, 12 if h > 60 else 9)
        tw = draw.textlength("26 YRS", font=lab)
        draw.text((x + int(w * 0.65) - tw / 2, y + int(h * 0.22)), "26 YRS",
                  font=lab, fill=(255, 255, 255))
        draw.text((x + int(w * 0.52), y + int(h * 0.78)), "5,412 CASES",
                  font=font(SANS_B, 9), fill=RED)
    else:  # 12: backpack, wheat, outback sun
        draw.rectangle([x, y, x + w, y + h], fill=(238, 230, 208))
        draw.ellipse([x + int(w * 0.78), y + int(h * 0.08),
                      x + int(w * 0.98), y + int(h * 0.48)], fill=(250, 172, 62))
        draw.rounded_rectangle([x + int(w * 0.08), y + int(h * 0.25),
                                x + int(w * 0.42), y + int(h * 0.92)], radius=12,
                               fill=(182, 92, 42))
        draw.rounded_rectangle([x + int(w * 0.16), y + int(h * 0.10),
                                x + int(w * 0.34), y + int(h * 0.30)], radius=8,
                               outline=(182, 92, 42), width=4)
        for sx in (0.55, 0.65):
            draw.line([x + int(w * sx), y + int(h * 0.92), x + int(w * sx), y + int(h * 0.34)],
                      fill=(172, 132, 42), width=3)
            for gy in (0.40, 0.55, 0.70):
                draw.ellipse([x + int(w * (sx - 0.04)), y + int(h * gy),
                              x + int(w * (sx + 0.04)), y + int(h * (gy + 0.10))],
                             fill=(222, 182, 62))


# ------------------------------------------------------------------- map
# Rough continent outlines in lon/lat, drawn equirectangular.
LAND = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 25), (-85, 20), (-90, 15), (-95, 18), (-105, 20), (-115, 28),
     (-125, 40), (-125, 48), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-70, 0), (-65, -5), (-60, -10), (-55, -20),
     (-50, -30), (-45, -25), (-40, -20), (-35, -8), (-40, 0), (-50, 0),
     (-60, 5), (-70, 10), (-78, 8)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 20), (43, 12), (48, 11), (51, 10), (45, 0), (40, -10), (35, -20),
     (30, -30), (20, -35), (15, -30), (12, -18), (13, -10), (9, 0), (0, 5),
     (-8, 5), (-13, 8)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 70), (25, 71), (18, 69),
     (12, 65), (5, 60), (0, 55), (-5, 50), (-10, 44)],
    [(30, 70), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (160, 65), (162, 60), (158, 52), (142, 50), (140, 40),
     (130, 33), (127, 35), (122, 30), (115, 22), (108, 12), (105, 8),
     (100, 8), (95, 15), (90, 22), (85, 20), (80, 10), (75, 8), (70, 20),
     (65, 25), (60, 25), (55, 26), (50, 29), (48, 30), (43, 35), (40, 36),
     (35, 36), (30, 41)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20)],
]


def project(lon, lat, mx, my, mw, mh):
    px = mx + (lon + 180.0) / 360.0 * mw
    py = my + (85.0 - lat) / 145.0 * mh
    return px, py


def draw_map(draw, mx, my, mw, mh):
    draw.rectangle([mx, my, mx + mw, my + mh], fill=(238, 233, 220),
                   outline=PANEL_LINE)
    inner = (mx + 4, my + 4, mw - 8, mh - 8)
    for poly in LAND:
        pts = [project(lon, lat, *inner) for lon, lat in poly]
        draw.polygon(pts, fill=MAP_FILL, outline=MAP_EDGE)
    for _n, _t, lon, lat in ALSO:
        px, py = project(lon, lat, *inner)
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(120, 115, 105))
    for n, region, _tag, _h, _d, lon, lat in MAINS:
        px, py = project(lon, lat, *inner)
        col = REGION_COLOUR[region]
        draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col,
                     outline=(255, 255, 255))
        fnt = font(SANS_B, 8)
        tw = draw.textlength(str(n), font=fnt)
        draw.text((px - tw / 2, py - 5), str(n), font=fnt, fill=(255, 255, 255))


# ---------------------------------------------------------------- panels
def draw_panel(draw, entry, x, y, w, h, lead):
    n, region, tag, headline, deck, _lon, _lat = entry
    col = REGION_COLOUR[region]
    art_h = 92 if lead else 46
    draw.rectangle([x, y, x + w, y + h], fill=PAPER, outline=PANEL_LINE)
    paint(draw, n, x + 1, y + 1, w - 2, art_h - 1)
    draw.line([x, y + art_h, x + w, y + art_h], fill=col, width=3)
    badge(draw, x + w - 20, y + art_h, n, col)
    ty = y + art_h + 10
    draw.text((x + 10, ty), region + " \u00b7 " + tag,
              font=font(SANS_B, 11), fill=col)
    head_size = 17 if lead else 15
    deck_size = 11 if lead else 10
    head_lines = balance_two(draw, headline, font(SERIF_B, head_size), w - 20)
    if head_lines is None:
        head_lines = fit_lines(draw, headline, font(SERIF_B, head_size), w - 20, 2)
    y2 = text_block(draw, x + 10, ty + 18, head_lines,
                    font(SERIF_B, head_size), INK, head_size + 4)
    deck_lines = fit_lines(draw, deck, font(SANS, deck_size), w - 20, 2)
    text_block(draw, x + 10, y2 + 3, deck_lines,
               font(SANS, deck_size), (70, 65, 55), deck_size + 4)


def centred(draw, cx, y, text, fnt, fill):
    tw = draw.textlength(text, font=fnt)
    draw.text((cx - tw / 2, y), text, font=fnt, fill=fill)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # Masthead: navy band, gold rule, title left, story count right.
    d.rectangle([0, 0, W, 102], fill=NAVY)
    d.rectangle([0, 102, W, 105], fill=GOLD)
    d.text((16, 10), "THE DAY IN WORLD NEWS", font=font(SANS_B, 15), fill=GOLD)
    d.text((16, 32), "Tuesday 17 November 2026",
           font=font(SERIF_B, 46), fill=(255, 255, 255))
    right = [("30 STORIES", font(SERIF_B, 27), GOLD, 10),
             ("6 CONTINENTS \u00b7 ONE DAY", font(SANS_B, 13), (255, 255, 255), 48)]
    for txt, fnt, fill, yy in right:
        d.text((W - 16 - d.textlength(txt, font=fnt), yy), txt, font=fnt, fill=fill)
    # Lead row (3 tall panels) + grid (3 rows x 3 cols).
    xs = [16, 349, 682]
    for i, x in enumerate(xs):
        draw_panel(d, MAINS[i], x, 108, 326, 194, lead=True)
    k = 3
    for row_y in (308, 452, 596):
        for x in xs:
            draw_panel(d, MAINS[k], x, row_y, 326, 138, lead=False)
            k += 1
    # Bottom: map left, also-on list right, legend under the map.
    d.text((16, 742), "WHERE IT HAPPENED", font=font(SANS_B, 14), fill=NAVY)
    d.text((466, 742), "ALSO ON TUESDAY 17 NOVEMBER",
           font=font(SANS_B, 14), fill=NAVY)
    d.line([16, 762, 1008, 762], fill=GOLD, width=2)
    draw_map(d, 16, 770, 430, 182)
    lx = 16
    for name, col in LEGEND:
        d.ellipse([lx, 960, lx + 9, 969], fill=col)
        d.text((lx + 13, 958), name, font=font(SANS, 10), fill=INK)
        lx += 13 + d.textlength(name, font=font(SANS, 10)) + 14
    for i, (num, txt, _lon, _lat) in enumerate(ALSO):
        col_x = 466 if i < 9 else 746
        row_y = 772 + (i % 9) * 20
        d.text((col_x, row_y), str(num) + ".", font=font(SANS_B, 10), fill=RED)
        also_fnt = font(SANS, 10)
        limit = 746 - (466 + 24) - 6
        shown = txt
        if d.textlength(shown, font=also_fnt) > limit:
            while shown and d.textlength(shown + "\u2026", font=also_fnt) > limit:
                shown = shown[:-1].rstrip()
            shown = shown + "\u2026"
        d.text((col_x + 24, row_y), shown, font=also_fnt, fill=INK)
    # Footer, centred, muted.
    centred(d, W / 2, 984,
            "Every story here was reported on Tuesday 17 November 2026; disputed claims are attributed.",
            font(SERIF, 11), MUTED)
    centred(d, W / 2, 1002,
            "Sources: AP, Reuters, AFP, BBC, Al Jazeera, UN News, WHO. Original drawings.",
            font(SERIF, 11), MUTED)
    img.save("entry.png")


if __name__ == "__main__":
    build()
