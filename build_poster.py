#!/usr/bin/env python3
"""Build the news-image-20261117 entry poster: 'Tuesday 17 November 2026'.

12 illustrated main panels + world map with numbered dots + 18-item also-on
strip = 30 stories, 6 continents. 1024x1024, deterministic, <=1 MiB.
Adapted from the proven news-image-01 v2 builder (masthead/grid/map), re-skinned
to the top-5 format formula of this competition (navy masthead band, gold count
line, numbered illustrated panels, honest 6-continent claim).
All facts verified against live sources on 2026-11-18; disputed claims are
attributed in the decks. No story is a recycle of a 13 Nov event.
"""
import os, hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (250, 246, 236)
PAPER = (247, 243, 233)
NAVY = (24, 48, 92)
NAVY2 = (31, 62, 116)
GOLD = (178, 140, 40)
GOLD_LT = (212, 175, 70)
INK = (28, 30, 34)
MUTED = (96, 92, 84)
RED = (176, 58, 46)
WHITE = (255, 255, 255)

REG = {
    "EUROPE": (31, 78, 121), "MIDDLE EAST": (176, 58, 46),
    "ASIA": (46, 125, 50), "AMERICAS": (125, 60, 152),
    "AFRICA": (20, 143, 119), "GLOBAL": (183, 149, 11),
    "OCEANIA": (202, 111, 30), "UNITED STATES": (125, 60, 152),
}

def font(name, size):
    paths = {
        "serif_b": ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
        "serif": ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"],
        "sans_b": ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
        "sans": ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
        "sans_i": ["/usr/share/fonts/truetype/noto/NotoSans-Italic.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"],
    }
    for p in paths[name]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def tw(d, s, f):
    return d.textlength(s, font=f)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_text(d, xy, s, f, fill=INK, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def rule(d, x0, x1, y, fill=GOLD, w=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)

def badge(d, x, y, n, color, r=11, fs=13):
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=color, outline=WHITE, width=2)
    draw_text(d, (x + r, y + r), str(n), font("sans_b", fs), fill=WHITE, anchor="mm")

# ---------------------------------------------------------------- illustrations
def ill_kerch(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(176, 214, 230))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(64, 118, 158))
    d.rectangle([x, y + h * 0.62, x + w, y + h * 0.66], fill=(150, 200, 220))
    # bridge deck left (standing) and right (standing), middle span fallen
    d.rectangle([x + 6, y + h * 0.30, x + w * 0.34, y + h * 0.36], fill=(40, 52, 70))
    d.rectangle([x + w * 0.66, y + h * 0.30, x + w - 6, y + h * 0.36], fill=(40, 52, 70))
    for bx in (x + 12, x + w * 0.24, x + w * 0.72, x + w - 18):
        d.rectangle([bx, y + h * 0.36, bx + 6, y + h * 0.62], fill=(40, 52, 70))
    # fallen span, tilted, half-submerged
    d.polygon([(x + w * 0.36, y + h * 0.52), (x + w * 0.62, y + h * 0.66),
               (x + w * 0.60, y + h * 0.72), (x + w * 0.34, y + h * 0.58)],
              fill=(90, 60, 50))
    # arch over the gap, cracked
    d.arc([x + w * 0.34, y + h * 0.02, x + w * 0.66, y + h * 0.42],
          start=180, end=360, fill=(24, 48, 92), width=5)
    d.line([(x + w * 0.50, y + h * 0.08), (x + w * 0.52, y + h * 0.16),
            (x + w * 0.48, y + h * 0.22)], fill=(24, 48, 92), width=3)
    # smoke + explosion burst at the gap
    for cx, cy, r, c in ((0.50, 0.22, 12, (240, 120, 40)),
                         (0.46, 0.16, 9, (240, 170, 60)),
                         (0.54, 0.14, 8, (120, 120, 120))):
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r, y + h * cy + r], fill=c)
    # drone silhouette top right
    d.ellipse([x + w * 0.82, y + h * 0.10, x + w * 0.88, y + h * 0.16], fill=(40, 52, 70))
    d.line([(x + w * 0.78, y + h * 0.13), (x + w * 0.92, y + h * 0.13)], fill=(40, 52, 70), width=2)

def ill_iran(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 200))
    # Gulf water bottom right
    d.polygon([(x + w * 0.55, y + h), (x + w, y + h * 0.45), (x + w, y + h)],
              fill=(120, 170, 205))
    # radar dish, big
    d.ellipse([x + w * 0.08, y + h * 0.14, x + w * 0.34, y + h * 0.58], outline=(24, 48, 92), width=5)
    d.line([(x + w * 0.21, y + h * 0.58), (x + w * 0.21, y + h * 0.88)], fill=(24, 48, 92), width=5)
    d.line([(x + w * 0.10, y + h * 0.88), (x + w * 0.32, y + h * 0.88)], fill=(24, 48, 92), width=5)
    d.arc([x + w * 0.30, y + h * 0.08, x + w * 0.50, y + h * 0.42],
          start=270, end=90, fill=(176, 58, 46), width=3)
    # drones incoming from right
    for cx, cy in ((0.72, 0.22), (0.84, 0.36), (0.66, 0.48)):
        d.ellipse([x + w * cx - 6, y + h * cy - 4, x + w * cx + 6, y + h * cy + 4], fill=(40, 52, 70))
        d.line([(x + w * cx - 12, y + h * cy), (x + w * cx + 12, y + h * cy)], fill=(40, 52, 70), width=2)
    # explosion burst on dish
    for cx, cy, r, c in ((0.21, 0.28, 11, (240, 120, 40)), (0.26, 0.20, 7, (240, 170, 60))):
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r, y + h * cy + r], fill=c)

def ill_trump(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 200))
    # three flag poles: US, China, Russia — tall, labels under flags
    flags = [((200, 40, 40), (255, 255, 255), "US"),
             ((222, 41, 16), (255, 235, 0), "CN"),
             ((255, 255, 255), (0, 57, 166), "RU")]
    for i, (c1, c2, lab) in enumerate(flags):
        fx = x + w * (0.14 + 0.28 * i)
        d.rectangle([fx, y + h * 0.08, fx + w * 0.20, y + h * 0.40], fill=c1, outline=(120, 110, 95))
        d.rectangle([fx, y + h * 0.24, fx + w * 0.20, y + h * 0.40], fill=c2, outline=(120, 110, 95))
        d.line([(fx, y + h * 0.06), (fx, y + h * 0.62)], fill=(90, 80, 65), width=3)
        draw_text(d, (fx + w * 0.10, y + h * 0.66), lab, font("sans_b", 12), fill=INK, anchor="ma")
    # plane silhouette top right
    d.polygon([(x + w * 0.78, y + h * 0.10), (x + w * 0.96, y + h * 0.16),
               (x + w * 0.78, y + h * 0.22)], fill=(40, 52, 70))
    d.line([(x + w * 0.80, y + h * 0.16), (x + w * 0.88, y + h * 0.06)], fill=(40, 52, 70), width=3)
    draw_text(d, (x + w * 0.50, y + h * 0.84), "MANILA  TO  SHENZHEN", font("sans_b", 12), fill=(24, 48, 92), anchor="ma")

def ill_nvidia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 200))
    # chip, bigger
    d.rectangle([x + w * 0.08, y + h * 0.16, x + w * 0.36, y + h * 0.84], fill=(24, 48, 92))
    d.rectangle([x + w * 0.15, y + h * 0.30, x + w * 0.29, y + h * 0.70], fill=(118, 185, 0))
    for px in (0.12, 0.18, 0.24, 0.30):
        d.line([(x + w * px, y + h * 0.06), (x + w * px, y + h * 0.16)], fill=(24, 48, 92), width=2)
        d.line([(x + w * px, y + h * 0.84), (x + w * px, y + h * 0.94)], fill=(24, 48, 92), width=2)
    # rising chart
    pts = [(0.44, 0.80), (0.54, 0.64), (0.64, 0.70), (0.74, 0.50), (0.84, 0.56), (0.94, 0.28)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        d.line([(x + w * ax, y + h * ay), (x + w * bx, y + h * by)], fill=(46, 125, 50), width=4)
    d.polygon([(x + w * 0.90, y + h * 0.28), (x + w * 0.99, y + h * 0.28),
               (x + w * 0.94, y + h * 0.14)], fill=(46, 125, 50))

def ill_ebola(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 200))
    # red virus orb with spikes
    cx, cy, r = x + w * 0.30, y + h * 0.50, h * 0.30
    for ang in range(0, 360, 30):
        import math
        a = math.radians(ang)
        d.line([(cx + math.cos(a) * r, cy + math.sin(a) * r),
                (cx + math.cos(a) * (r + 8), cy + math.sin(a) * (r + 8))],
               fill=(176, 58, 46), width=3)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(176, 58, 46))
    d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.1, cy + r * 0.1], fill=(220, 110, 90))
    # case-count, one big line + one small line
    draw_text(d, (x + w * 0.74, y + h * 0.14), "11,000+", font("sans_b", 19), fill=(176, 58, 46), anchor="ma")
    draw_text(d, (x + w * 0.74, y + h * 0.58), "CASES · 5,400 DEAD", font("sans_b", 10), fill=INK, anchor="ma")

def ill_mongolia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 200))
    # parliament building
    d.rectangle([x + w * 0.10, y + h * 0.42, x + w * 0.62, y + h * 0.86], fill=(24, 48, 92))
    d.polygon([(x + w * 0.06, y + h * 0.42), (x + w * 0.36, y + h * 0.16),
               (x + w * 0.66, y + h * 0.42)], fill=(31, 62, 116))
    for i in range(4):
        d.rectangle([x + w * (0.15 + 0.11 * i), y + h * 0.52, x + w * (0.20 + 0.11 * i), y + h * 0.86],
                    fill=(212, 175, 70))
    # $25M tag, plain red text (no box — fits the 46px strip)
    draw_text(d, (x + w * 0.81, y + h * 0.18), "$25M", font("sans_b", 18), fill=(176, 58, 46), anchor="ma")
    draw_text(d, (x + w * 0.81, y + h * 0.60), "GRAFT CLAIM", font("sans_b", 10), fill=INK, anchor="ma")

def ill_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 200))
    # globe
    cx, cy, r = x + w * 0.28, y + h * 0.50, h * 0.32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 150, 200))
    d.ellipse([cx - r * 0.55, cy - r * 0.75, cx + r * 0.55, cy - r * 0.15], fill=(70, 160, 90))
    d.ellipse([cx - r * 0.75, cy + r * 0.15, cx - r * 0.05, cy + r * 0.70], fill=(70, 160, 90))
    # thermometer
    d.rectangle([x + w * 0.58, y + h * 0.16, x + w * 0.66, y + h * 0.72], fill=WHITE, outline=(24, 48, 92), width=2)
    d.ellipse([x + w * 0.55, y + h * 0.64, x + w * 0.69, y + h * 0.88], fill=(176, 58, 46))
    d.rectangle([x + w * 0.60, y + h * 0.42, x + w * 0.64, y + h * 0.72], fill=(176, 58, 46))
    # split arrows: phase out vs transition
    d.line([(x + w * 0.74, y + h * 0.30), (x + w * 0.94, y + h * 0.30)], fill=(46, 125, 50), width=3)
    d.polygon([(x + w * 0.94, y + h * 0.30), (x + w * 0.88, y + h * 0.22),
               (x + w * 0.88, y + h * 0.38)], fill=(46, 125, 50))
    d.line([(x + w * 0.74, y + h * 0.58), (x + w * 0.94, y + h * 0.58)], fill=(183, 149, 11), width=3)
    d.polygon([(x + w * 0.94, y + h * 0.58), (x + w * 0.88, y + h * 0.50),
               (x + w * 0.88, y + h * 0.66)], fill=(183, 149, 11))
    draw_text(d, (x + w * 0.84, y + h * 0.10), "1.5°C", font("sans_b", 12), fill=(176, 58, 46), anchor="ma")

def ill_japan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(176, 214, 230))
    # rising sun disc
    d.ellipse([x + w * 0.68, y + h * 0.10, x + w * 0.96, y + h * 0.52], fill=(176, 58, 46))
    # two fighter jets
    for jx, jy, sc in ((0.12, 0.30, 1.0), (0.30, 0.55, 0.8)):
        bx, by = x + w * jx, y + h * jy
        d.polygon([(bx, by), (bx + 34 * sc, by + 8 * sc), (bx, by + 16 * sc)], fill=(40, 52, 70))
        d.polygon([(bx + 10 * sc, by + 2 * sc), (bx + 22 * sc, by - 8 * sc),
                   (bx + 26 * sc, by + 2 * sc)], fill=(40, 52, 70))
        d.line([(bx, by + 8 * sc), (bx - 12 * sc, by + 8 * sc)], fill=(240, 170, 60), width=2)
    # radar arcs from ground station
    d.arc([x + w * 0.05, y + h * 0.55, x + w * 0.45, y + h * 1.15],
          start=270, end=360, fill=(24, 48, 92), width=2)
    d.arc([x + w * 0.12, y + h * 0.62, x + w * 0.38, y + h * 1.05],
          start=270, end=360, fill=(24, 48, 92), width=2)

def ill_dow(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 200))
    # falling red chart
    pts = [(0.08, 0.28), (0.22, 0.36), (0.36, 0.32), (0.50, 0.52), (0.64, 0.48), (0.78, 0.70), (0.92, 0.78)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        d.line([(x + w * ax, y + h * ay), (x + w * bx, y + h * by)], fill=(176, 58, 46), width=4)
    d.polygon([(x + w * 0.92, y + h * 0.78), (x + w * 0.84, y + h * 0.70),
               (x + w * 0.98, y + h * 0.68)], fill=(176, 58, 46))
    # gridlines
    for gy in (0.25, 0.5, 0.75):
        d.line([(x + w * 0.06, y + h * gy), (x + w * 0.94, y + h * gy)], fill=(210, 205, 190), width=1)

def ill_pope(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 200))
    # St Peter's dome silhouette
    d.rectangle([x + w * 0.14, y + h * 0.52, x + w * 0.56, y + h * 0.86], fill=(24, 48, 92))
    d.pieslice([x + w * 0.22, y + h * 0.16, x + w * 0.48, y + h * 0.56], start=180, end=360, fill=(31, 62, 116))
    d.rectangle([x + w * 0.32, y + h * 0.08, x + w * 0.38, y + h * 0.18], fill=(212, 175, 70))
    d.rectangle([x + w * 0.30, y + h * 0.62, x + w * 0.40, y + h * 0.86], fill=(212, 175, 70))
    # Vatican flag (yellow/white)
    d.rectangle([x + w * 0.64, y + h * 0.20, x + w * 0.80, y + h * 0.44], fill=(240, 210, 90), outline=(120, 110, 95))
    d.rectangle([x + w * 0.80, y + h * 0.20, x + w * 0.96, y + h * 0.44], fill=WHITE, outline=(120, 110, 95))
    d.line([(x + w * 0.64, y + h * 0.18), (x + w * 0.64, y + h * 0.86)], fill=(90, 80, 65), width=3)
    # crowd dots
    for i, cx in enumerate((0.68, 0.78, 0.88)):
        d.ellipse([x + w * cx - 4, y + h * 0.68 - 4, x + w * cx + 4, y + h * 0.68 + 4],
                  fill=(176, 58, 46) if i == 1 else (24, 48, 92))

def ill_measles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 200))
    # red measles virus orb
    import math
    cx, cy, r = x + w * 0.28, y + h * 0.50, h * 0.30
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([(cx + math.cos(a) * r, cy + math.sin(a) * r),
                (cx + math.cos(a) * (r + 7), cy + math.sin(a) * (r + 7))],
               fill=(176, 58, 46), width=3)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(176, 58, 46))
    d.ellipse([cx - r * 0.4, cy - r * 0.4, cx + r * 0.15, cy + r * 0.15], fill=(220, 110, 90))
    # shield, plain — year range as one line
    d.polygon([(x + w * 0.72, y + h * 0.14), (x + w * 0.92, y + h * 0.14),
               (x + w * 0.92, y + h * 0.48), (x + w * 0.82, y + h * 0.66),
               (x + w * 0.62, y + h * 0.48)], fill=(24, 48, 92))
    draw_text(d, (x + w * 0.77, y + h * 0.26), "26 YRS", font("sans_b", 12), fill=WHITE, anchor="ma")
    draw_text(d, (x + w * 0.77, y + h * 0.72), "5,412 CASES", font("sans_b", 11), fill=(176, 58, 46), anchor="ma")

def ill_aus(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 215, 160))
    # outback sun
    d.ellipse([x + w * 0.68, y + h * 0.10, x + w * 0.92, y + h * 0.46], fill=(240, 150, 40))
    # red ground
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(176, 90, 50))
    # backpack
    d.rounded_rectangle([x + w * 0.14, y + h * 0.30, x + w * 0.42, y + h * 0.82],
                        radius=8, fill=(24, 48, 92))
    d.rounded_rectangle([x + w * 0.20, y + h * 0.20, x + w * 0.36, y + h * 0.32],
                        radius=6, fill=(31, 62, 116))
    d.rectangle([x + w * 0.14, y + h * 0.50, x + w * 0.42, y + h * 0.58], fill=(212, 175, 70))
    # wheat stalks
    for sx in (0.52, 0.58, 0.64):
        d.line([(x + w * sx, y + h * 0.82), (x + w * sx, y + h * 0.42)], fill=(150, 120, 40), width=3)
        d.ellipse([x + w * sx - 4, y + h * 0.42 - 8, x + w * sx + 4, y + h * 0.42 + 8], fill=(212, 175, 70))

# ---------------------------------------------------------------- story data
# (n, region, tag, headline, deck, illustrator)
MAINS = [
    (1, "EUROPE", "WAR",
     "UKRAINE BRINGS DOWN A SPAN OF THE KERCH BRIDGE",
     "Road arch drops into the strait in a seven-stage strike, a day after Russia hit Kyiv's bridges.",
     ill_kerch),
    (2, "MIDDLE EAST", "WAR",
     "IRAN FIRES DRONES AT A US RADAR IN BAHRAIN",
     "Bahrain says it intercepted the drones; the US then struck a missile site on Qeshm Island.",
     ill_iran),
    (3, "ASIA", "DIPLOMACY",
     "TRUMP LANDS IN MANILA; NEXT, XI AND PUTIN",
     "Quad meets for the first time in two years; Thursday he joins Xi and Putin in Shenzhen — a first.",
     ill_trump),
    (4, "UNITED STATES", "TECH",
     "NVIDIA POSTS A RECORD $115.8BN QUARTER",
     "Revenue $115.8bn, up 103%; first results since Huang quit. The board will not reinstate him.",
     ill_nvidia),
    (5, "AFRICA", "HEALTH",
     "EBOLA CASES MORE THAN DOUBLE IN DR CONGO",
     "WHO counts 11,000+ cases and 5,400 deaths in DR Congo; children are a third of the dead.",
     ill_ebola),
    (6, "ASIA", "POLITICS",
     "MONGOLIA'S PRESIDENT SAYS HE WILL RESIGN",
     "Khurelsukh denies taking $25m over a railway deal; parliament must accept his resignation.",
     ill_mongolia),
    (7, "GLOBAL", "CLIMATE",
     "COP31 DRAFT SPLITS THE WORLD ON FOSSIL FUELS",
     "Draft offers 'phase out' or 'transitioning away'; the EU wants the strongest clean-energy signal.",
     ill_cop31),
    (8, "ASIA", "DEFENCE",
     "JAPAN SCRAMBLES JETS AT RUSSIAN INCURSION",
     "Two suspected Russian planes enter its airspace for three minutes each; Tokyo protests.",
     ill_japan),
    (9, "UNITED STATES", "MARKETS",
     "DOW SINKS 849 POINTS",
     "Fourth straight fall; the S&P closes at its lowest since July as software stocks slide.",
     ill_dow),
    (10, "EUROPE", "RELIGION",
     "POPE LEO XIV FLIES HOME AFTER 12 DAYS",
     "Lands in Rome at 8:48am after 12 days in Latin America; his lung tumour was 'entirely contained'.",
     ill_pope),
    (11, "AMERICAS", "HEALTH",
     "US LOSES MEASLES-FREE STATUS AFTER 26 YEARS",
     "PAHO ends the US elimination status held since 2000; 5,412 cases in 2026, the most in 35 years.",
     ill_measles),
    (12, "OCEANIA", "POLICY",
     "AUSTRALIA TIGHTENS BACKPACKER VISA RULES",
     "Four months of rural work, up from three, for a second-year visa from March.",
     ill_aus),
]

ALSO_ON = [
    (13, "Russia says it downed 1,441 drones in two nights"),
    (14, "Ukraine: Europeans join peace talks"),
    (15, "IMF: Ukraine may get $1.6bn more in aid"),
    (16, "Gaza: Berlin urges far more aid"),
    (17, "Syria: UN says ~4m have returned home"),
    (18, "Jordan and Iraq block Telegram"),
    (19, "Pakistan seeks to revive US–Iran talks"),
    (20, "Saudis replace Yemen coalition chief"),
    (21, "Serbia: students lead new parliament"),
    (22, "Poland: Tusk survives confidence vote"),
    (23, "COP31: Brazil says draft falls short"),
    (24, "WHO: superbugs could kill 39m+ by 2050"),
    (25, "Third US carrier arrives in the Gulf"),
    (26, "US data centres emit like Denmark"),
    (27, "Ecuador fishermen sue US over strike"),
    (28, "Mexico: journalist found dead in Acapulco"),
    (29, "PNG defends closing Taiwan office"),
    (30, "UN rights chief warns over Rwanda hub"),
]

# (lon, lat) for the 12 main dots
MAIN_DOTS = [(36.5, 45.3), (50.6, 26.2), (121.0, 14.6), (-121.0, 37.4),
             (23.0, -3.0), (106.9, 47.9), (30.7, 36.9), (130.4, 33.6),
             (-74.0, 40.7), (12.5, 41.9), (-84.4, 33.7), (149.1, -35.3)]
# (lon, lat) for the also-on dots, keyed by story number
ALSO_DOTS = {13: (37.6, 55.8), 14: (30.5, 50.4), 15: (-77.0, 38.9),
             16: (13.4, 52.5), 17: (36.3, 33.5), 18: (35.9, 31.9),
             19: (73.1, 33.7), 20: (46.7, 24.7), 21: (20.5, 44.8),
             22: (21.0, 52.2), 23: (-47.9, -15.8), 24: (6.1, 46.2),
             25: (51.5, 27.5), 26: (-78.0, 38.5), 27: (-78.5, -0.2),
             28: (-99.1, 19.4), 29: (147.2, -9.5), 30: (30.1, -1.9)}

CONTINENTS = {
    "NA": [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-80, 73),
           (-65, 60), (-55, 47), (-60, 45), (-70, 42), (-75, 35), (-80, 26),
           (-82, 28), (-90, 21), (-95, 19), (-97, 16), (-92, 14), (-86, 12),
           (-83, 9), (-80, 8), (-78, 7), (-83, 9), (-90, 14), (-97, 16),
           (-105, 20), (-110, 23), (-114, 29), (-120, 34), (-125, 40),
           (-124, 48), (-130, 55), (-140, 60), (-152, 58), (-165, 60), (-168, 66)],
    "SA": [(-80, 8), (-77, 4), (-79, -3), (-81, -6), (-77, -12), (-72, -18),
           (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50),
           (-68, -55), (-66, -55), (-65, -45), (-62, -41), (-58, -34),
           (-52, -32), (-48, -27), (-41, -22), (-39, -17), (-35, -9),
           (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-54, 2), (-60, 5),
           (-62, 9), (-70, 11), (-77, 8), (-80, 8)],
    "EU": [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-2, 48), (0, 50),
           (2, 51), (5, 53), (8, 55), (8, 57), (10, 58), (13, 56),
           (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (32, 66),
           (35, 68), (40, 68), (44, 66), (48, 64), (44, 60), (40, 58),
           (38, 55), (35, 52), (33, 48), (30, 46), (28, 45), (23, 44),
           (19, 42), (16, 40), (12, 42), (10, 44), (7, 44), (3, 42),
           (0, 38), (-5, 36), (-10, 36)],
    "AF": [(-6, 35), (10, 37), (20, 32), (30, 31), (32, 31), (35, 28),
           (38, 22), (39, 15), (43, 12), (51, 11), (51, 2), (48, -2),
           (41, -10), (40, -15), (36, -18), (33, -26), (28, -33),
           (20, -35), (17, -32), (12, -18), (13, -12), (9, -1),
           (9, 4), (4, 6), (-8, 5), (-13, 8), (-17, 15), (-16, 20),
           (-15, 27), (-10, 31), (-6, 35)],
    "AS": [(35, 36), (36, 31), (40, 30), (44, 29), (48, 29), (50, 26),
           (54, 24), (57, 26), (61, 25), (66, 25), (70, 22), (72, 20),
           (77, 13), (80, 10), (84, 15), (89, 21), (92, 21), (94, 17),
           (98, 10), (101, 8), (104, 2), (106, -3), (110, -7), (114, -8),
           (118, -10), (120, -5), (123, 1), (126, 6), (130, 10), (127, 15),
           (124, 25), (121, 30), (120, 35), (122, 40), (127, 40), (130, 42),
           (135, 44), (140, 46), (142, 50), (140, 55), (142, 60), (158, 62),
           (162, 66), (178, 66), (170, 68), (160, 69), (150, 70), (140, 72),
           (130, 71), (120, 73), (110, 74), (100, 76), (90, 75), (80, 73),
           (70, 72), (60, 69), (55, 68), (50, 66), (45, 67), (40, 68),
           (35, 66), (32, 60), (30, 55), (33, 50), (36, 44), (35, 36)],
    "OC": [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33),
           (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
           (153, -32), (153, -27), (150, -23), (146, -19), (142, -11),
           (142, -15), (137, -17), (136, -15), (132, -12), (126, -14),
           (122, -17), (117, -20), (113, -22)],
}

# ---------------------------------------------------------------- layout
def panel(d, x, y, w, h, n, region, tag, headline, deck, ill, lead=False):
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=(200, 195, 185), width=1)
    color = REG[region]
    ill_h = 92 if lead else 46
    ill(d, x + 1, y + 1, w - 2, ill_h)
    d.rectangle([x, y + ill_h, x + w, y + ill_h + 2], fill=color)
    badge(d, x + w - 30, y + ill_h - 11, n, color, r=12 if lead else 11,
          fs=14 if lead else 12)
    ty = y + ill_h + 6
    draw_text(d, (x + 10, ty), f"{region} · {tag}", font("sans_b", 10 if lead else 9), fill=color)
    hl_f = font("serif_b", 20 if lead else 16)
    lines = wrap(d, headline, hl_f, w - 20)
    hy = ty + (14 if lead else 14)
    for ln in lines[:2]:
        draw_text(d, (x + 10, hy), ln, hl_f, fill=INK)
        hy += 22 if lead else 19
    dk_f = font("sans", 12 if lead else 11)
    dlines = wrap(d, deck, dk_f, w - 20)
    dy = hy + 2
    for ln in dlines[:2 if lead else 2]:
        draw_text(d, (x + 10, dy), ln, dk_f, fill=(60, 58, 52))
        dy += 14 if lead else 14

def masthead(d):
    d.rectangle([0, 0, W, 98], fill=NAVY)
    d.rectangle([0, 98, W, 101], fill=GOLD)
    draw_text(d, (14, 10), "THE DAY IN WORLD NEWS", font("sans_b", 14), fill=GOLD_LT)
    draw_text(d, (14, 30), "Tuesday 17 November 2026", font("serif_b", 48), fill=WHITE)
    draw_text(d, (W - 14, 22), "30 STORIES", font("serif_b", 26), fill=GOLD_LT, anchor="ra")
    draw_text(d, (W - 14, 56), "6 CONTINENTS · ONE DAY", font("sans_b", 14), fill=WHITE, anchor="ra")

def world_map(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(235, 230, 218),
                outline=(200, 195, 185), width=1)
    def px(lon): return x0 + (lon + 170) / 360 * w
    def py(lat): return y0 + (85 - lat) / 145 * h
    for pts in CONTINENTS.values():
        d.polygon([(px(lo), py(la)) for lo, la in pts], fill=(196, 190, 175),
                  outline=(150, 145, 135))
    for n, (lo, la) in enumerate(MAIN_DOTS, 1):
        reg = MAINS[n - 1][1]
        cx, cy = px(lo), py(la)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=REG[reg], outline=WHITE, width=2)
        draw_text(d, (cx, cy), str(n), font("sans_b", 8), fill=WHITE, anchor="mm")
    for n, (lo, la) in ALSO_DOTS.items():
        cx, cy = px(lo), py(la)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(90, 88, 80), outline=WHITE, width=1)

def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    masthead(d)
    # lead row: 3 panels
    pw, gap, x0 = 326, 6, 6
    ly, lh = 108, 194
    for i, m in enumerate(MAINS[:3]):
        panel(d, x0 + i * (pw + gap), ly, pw, lh, m[0], m[1], m[2], m[3], m[4], m[5], lead=True)
    # grid rows: 3 rows x 3 cols
    gy, gh = 308, 138
    for r in range(3):
        for c in range(3):
            m = MAINS[3 + r * 3 + c]
            panel(d, x0 + c * (pw + gap), gy + r * (gh + 6), pw, gh,
                  m[0], m[1], m[2], m[3], m[4], m[5])
    # bottom: map + also-on
    by = 740
    draw_text(d, (6, by), "WHERE IT HAPPENED", font("sans_b", 14), fill=NAVY)
    rule(d, 6, 1018, by + 20, fill=GOLD, w=2)
    world_map(d, 6, by + 28, 430, 182)
    # legend under map
    lx, ly2 = 6, by + 214
    for name, col in [("Europe", REG["EUROPE"]), ("Middle East", REG["MIDDLE EAST"]),
                      ("Asia", REG["ASIA"]), ("Americas", REG["AMERICAS"]),
                      ("Africa", REG["AFRICA"]), ("Oceania", REG["OCEANIA"])]:
        d.ellipse([lx, ly2, lx + 9, ly2 + 9], fill=col)
        draw_text(d, (lx + 12, ly2 - 1), name, font("sans", 10), fill=INK)
        lx += 12 + int(d.textlength(name, font=font("sans", 10))) + 12
    # also-on list
    ax = 452
    draw_text(d, (ax, by), "ALSO ON TUESDAY 17 NOVEMBER", font("sans_b", 14), fill=NAVY)
    rule(d, ax, 1018, by + 20, fill=GOLD, w=2)
    ay = by + 28
    col_w = 283
    for i, (n, text) in enumerate(ALSO_ON):
        col = i // 9
        row = i % 9
        tx = ax + col * col_w
        ty = ay + row * 20
        draw_text(d, (tx, ty), f"{n}.", font("sans_b", 11), fill=RED)
        draw_text(d, (tx + 22, ty), text, font("sans", 11), fill=INK)
    # footer
    draw_text(d, (W // 2, 994), "Every story here was reported on Tuesday 17 November 2026; disputed claims are attributed.",
              font("sans_i", 11), fill=MUTED, anchor="ma")
    draw_text(d, (W // 2, 1008), "Sources: AP, Reuters, AFP, BBC, Al Jazeera, UN News, WHO. Original drawings.",
              font("sans", 10), fill=MUTED, anchor="ma")
    return img

if __name__ == "__main__":
    out = os.environ.get("OUT", "entry.png")
    img = build()
    img.save(out, optimize=True)
    print(out, img.size, os.path.getsize(out), "bytes")
    print("sha256", hashlib.sha256(open(out, "rb").read()).hexdigest())
