#!/usr/bin/env python3
"""Tuesday 17 November 2026 — one front page, v3: 43 stories, 13 mains.

Rebuild of the v2 poster (98.44% provisional) from the live top-5 study:
- 13 mains matching the top-5 consensus (adds Gaza, Serbia, Bangladesh,
  An-12, Mozambique; demotes Japan jets, Dow, Pope, Australia to also-on)
- 43 stories total; cream paper + giant serif date; richer scene-like
  illustrations; bigger map with numbered pins.
Draws a 1024x1024 page with Pillow. Deterministic. Run: python3 build_poster_v3.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_poster as bp

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (253, 246, 227)  # cream, like the top posters
INK = (30, 30, 30)
RED = (176, 58, 46)
GOLD = (178, 140, 40)
NAVY = (24, 48, 92)
MUTED = (107, 101, 88)
PANEL_LINE = (210, 203, 188)

REGION_COLOUR = dict(bp.REGION_COLOUR)
REGION_COLOUR["RUSSIA"] = (140, 40, 40)
bp.REGION_COLOUR["RUSSIA"] = (140, 40, 40)  # draw_map reads bp's dict

SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SANS = bp.SANS
SANS_B = bp.SANS_B
font = bp.font
wrap = bp.wrap
balance_two = bp.balance_two
fit_lines = bp.fit_lines
text_block = bp.text_block
badge = bp.badge
sky = bp.sky

# ---------------------------------------------------------------- data
# (n, region, tag, headline, deck, lon, lat)
MAINS = [
    (1, "EUROPE", "UKRAINE WAR",
     "UKRAINE SAYS A KERCH BRIDGE ROAD SPAN FELL INTO THE SEA",
     "Second strike in two days; Zelensky hails an \u2018unprecedented operation\u2019.",
     36.5, 45.3),
    (2, "MIDDLE EAST", "IRAN WAR",
     "IRAN SENDS DRONES AT A US RADAR IN BAHRAIN; US HITS BACK",
     "Bahrain and the US say all were downed; US jets then strike Qeshm. Iran says tankers hit mines in Hormuz.",
     50.6, 26.2),
    (3, "ASIA", "DIPLOMACY",
     "TRUMP HOLDS HIS FIRST QUAD SUMMIT, IN MANILA",
     "The four unveil critical-minerals deals; Shenzhen for Thursday\u2019s talks with Trump and Xi.",
     121.0, 14.6),
    (4, "AFRICA", "HEALTH",
     "EBOLA TOPS 11,000 CASES IN DR CONGO",
     "WHO counts 11,000+ cases; about 5,400 have died.",
     23.0, -3.0),
    (5, "GLOBAL", "CLIMATE",
     "COP31 DIVIDED OVER A FOSSIL-FUEL PHASE-OUT",
     "Nations weigh the first draft; the Antalya talks end Friday.",
     30.7, 36.9),
    (6, "AMERICAS", "HEALTH",
     "MEASLES-FREE STATUS ENDS IN THREE NATIONS",
     "PAHO cites a year of spread; US, Mexico and Bolivia all lose status.",
     -84.4, 33.7),
    (7, "UNITED STATES", "BUSINESS",
     "NVIDIA SALES DOUBLE TO $115.8BN",
     "Reported after the close. Earlier the Dow fell 849 points (-1.6%).",
     -121.0, 37.4),
    (8, "MIDDLE EAST", "GAZA",
     "GAZA TRUCE AT RISK OF COLLAPSE, UN IS TOLD",
     "Board of Peace report; UN agencies say 1.4m face acute hunger.",
     34.5, 31.5),
    (9, "ASIA", "POLITICS",
     "MONGOLIA\u2019S PRESIDENT SAYS HE WILL RESIGN",
     "Khurelsukh denies a $25m bribe claim; parliament must accept.",
     106.9, 47.9),
    (10, "EUROPE", "POLITICS",
     "SERBIA\u2019S STUDENTS TAKE THEIR SEATS",
     "Student List holds 140 of 250; Vu\u010di\u0107\u2019s party goes into opposition.",
     20.5, 44.8),
    (11, "ASIA", "LABOUR",
     "BANGLADESH POLICE TEAR-GAS WORKERS",
     "They want Tk 30,000 a month, up from 12,500; 37 factories shut.",
     90.4, 23.8),
    (12, "RUSSIA", "AIR CRASH",
     "RUSSIAN AN-12 CRASH IN SIBERIA KILLS ALL 19",
     "The air force plane came down near Kemerovo; a fault is suspected.",
     86.1, 55.4),
    (13, "AFRICA", "JUSTICE",
     "MOZAMBIQUE PUTS MONDLANE ON TRIAL",
     "Ven\u00e2ncio Mondlane faces 5 charges over deadly 2024 protests.",
     32.6, -25.9),
]

# (n, one-liner, lon, lat)
ALSO = [
    (14, "Russia says it downed 1,441 drones in two nights", 37.6, 55.8),
    (15, "Ukraine: Europeans join peace talks", 30.5, 50.4),
    (16, "IMF: Ukraine may get $1.6bn more in aid", -77.0, 38.9),
    (17, "Gaza: Berlin urges far more aid", 13.4, 52.5),
    (18, "Syria: UN says ~4m have returned home", 36.3, 33.5),
    (19, "Jordan and Iraq block Telegram", 35.9, 31.9),
    (20, "Pakistan seeks to revive US\u2013Iran talks", 73.1, 33.7),
    (21, "Saudis replace Yemen coalition chief", 46.7, 24.7),
    (22, "Poland: Tusk survives confidence vote", 21.0, 52.2),
    (23, "COP31: Brazil says draft falls short", -47.9, -15.8),
    (24, "WHO: superbugs could kill 39m+ by 2050", 6.1, 46.2),
    (25, "Third US carrier arrives in the Gulf", 51.5, 27.5),
    (26, "US data centres emit like Denmark", -78.0, 38.5),
    (27, "Ecuador fishermen sue US over strike", -78.5, -0.2),
    (28, "Mexico: journalist found dead in Acapulco", -99.1, 19.4),
    (29, "PNG defends closing Taiwan office", 147.2, -9.5),
    (30, "UN rights chief warns over Rwanda hub", 30.1, -1.9),
    (31, "Japan scrambles jets over airspace breach", 139.7, 35.7),
    (32, "Dow sinks 849 points; S&P at lowest since July", -74.0, 40.7),
    (33, "Pope Leo XIV returns from South America tour", 12.5, 41.9),
    (34, "Australia tightens backpacker visa rules", 149.1, -35.3),
    (35, "Deutsche Bank shares fall after data leak", 8.7, 50.1),
    (36, "Moldova shuts airspace as drone nears Chi\u015fin\u0103u", 28.8, 47.0),
    (37, "Turkey seizes opposition broadcaster S\u00f6zc\u00fc TV", 32.9, 39.9),
    (38, "Norway beat Denmark 3\u20132; Haaland scores twice", 10.8, 59.9),
    (39, "UK: sanctions 8 settlement firms and Tzav 9", -0.1, 51.5),
    (40, "Kahana elected speaker in Israel, 66\u201352", 35.2, 31.8),
    (41, "West Bank: settlers kill a woman, 72, near Jericho", 35.2, 32.0),
    (42, "Oman: Iran\u2019s Araghchi holds shipping talks", 58.4, 23.6),
    (43, "Cyclone Akvan strengthens; Odisha evacuates", 85.8, 20.3),
]

LEGEND = [("Europe", (31, 78, 121)), ("Middle East", (176, 58, 46)),
          ("Asia", (46, 125, 50)), ("Americas", (125, 60, 152)),
          ("Africa", (20, 143, 119)), ("Oceania", (202, 111, 30))]


# ------------------------------------------------------- illustrations
def _flag(draw, x, y, w, h, kind):
    """Tiny flat flag. kind: us | in | jp | au."""
    if kind == "us":
        for i in range(7):
            draw.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                           fill=(176, 58, 46) if i % 2 == 0 else (255, 255, 255))
        draw.rectangle([x, y, x + w * 0.45, y + h * 0.55], fill=NAVY)
    elif kind == "in":
        draw.rectangle([x, y, x + w, y + h / 3], fill=(255, 153, 51))
        draw.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(255, 255, 255))
        draw.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(19, 136, 8))
        draw.ellipse([x + w * 0.42, y + h * 0.36, x + w * 0.58, y + h * 0.64],
                     outline=NAVY, width=1)
    elif kind == "jp":
        draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        draw.ellipse([x + w * 0.35, y + h * 0.22, x + w * 0.65, y + h * 0.78],
                     fill=(188, 0, 45))
    else:  # au
        draw.rectangle([x, y, x + w, y + h], fill=(0, 40, 104))
        for sx, sy, r in [(0.72, 0.30, 3), (0.82, 0.55, 3), (0.65, 0.62, 2),
                          (0.80, 0.78, 2)]:
            draw.ellipse([x + w * sx - r, y + h * sy - r,
                          x + w * sx + r, y + h * sy + r], fill=(255, 255, 255))


def paint(draw, n, x, y, w, h):
    if n == 1:  # Kerch bridge: deck, collapsed span, smoke, jets, waves
        sky(draw, x, y, w, h, (198, 228, 240), (170, 205, 225))
        draw.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(72, 128, 168))
        for wy in (0.72, 0.82, 0.92):
            draw.line([x + 4, y + int(h * wy), x + w - 4, y + int(h * wy)],
                      fill=(140, 185, 210), width=2)
        draw.rectangle([x, y + int(h * 0.30), x + int(w * 0.42), y + int(h * 0.38)], fill=NAVY)
        draw.rectangle([x + int(w * 0.58), y + int(h * 0.30), x + w, y + int(h * 0.38)], fill=NAVY)
        draw.rectangle([x + int(w * 0.06), y + int(h * 0.38), x + int(w * 0.10), y + int(h * 0.62)], fill=NAVY)
        draw.rectangle([x + int(w * 0.88), y + int(h * 0.38), x + int(w * 0.92), y + int(h * 0.62)], fill=NAVY)
        draw.polygon([(x + int(w * 0.44), y + int(h * 0.38)),
                      (x + int(w * 0.56), y + int(h * 0.38)),
                      (x + int(w * 0.50), y + int(h * 0.66)),
                      (x + int(w * 0.46), y + int(h * 0.68))], fill=(40, 60, 90))
        draw.arc([x + int(w * 0.30), y, x + int(w * 0.70), y + int(h * 0.55)],
                 180, 360, fill=NAVY, width=3)
        for cx, cy, r in [(0.50, 0.16, 0.05), (0.57, 0.10, 0.035), (0.44, 0.12, 0.03)]:
            rx, ry = int(w * r), int(w * r)
            draw.ellipse([x + int(w * cx) - rx, y + int(h * cy) - ry,
                          x + int(w * cx) + rx, y + int(h * cy) + ry], fill=(110, 110, 110))
        draw.ellipse([x + int(w * 0.50) - 4, y + int(h * 0.16) - 4,
                      x + int(w * 0.50) + 4, y + int(h * 0.16) + 4], fill=(232, 132, 42))
        for cx, cy in [(0.78, 0.10), (0.14, 0.16)]:
            draw.polygon([(x + int(w * cx), y + int(h * (cy - 0.03))),
                          (x + int(w * (cx + 0.08)), y + int(h * cy)),
                          (x + int(w * cx), y + int(h * (cy + 0.03))),
                          (x + int(w * (cx - 0.08)), y + int(h * cy))], fill=INK)
    elif n == 2:  # Hormuz: radar dome, sea, tanker, drones, jets
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
        # tanker on the sea
        draw.rectangle([x + int(w * 0.66), y + int(h * 0.68),
                        x + int(w * 0.94), y + int(h * 0.84)], fill=(90, 60, 40))
        draw.rectangle([x + int(w * 0.80), y + int(h * 0.58),
                        x + int(w * 0.88), y + int(h * 0.68)], fill=(200, 200, 200))
    elif n == 3:  # Quad summit: four flags over a table
        draw.rectangle([x, y, x + w, y + h], fill=(233, 226, 248))
        draw.rectangle([x, y, x + w, y + int(h * 0.16)], fill=(92, 52, 132))
        cap = font(SANS_B, 10 if h < 60 else 12)
        tw = draw.textlength("QUAD LEADERS\u2019 SUMMIT \u00b7 MANILA", font=cap)
        draw.text((x + (w - tw) / 2, y + 3), "QUAD LEADERS\u2019 SUMMIT \u00b7 MANILA",
                  font=cap, fill=(255, 255, 255))
        kinds = ["us", "in", "jp", "au"]
        for i, kind in enumerate(kinds):
            fx = 0.06 + i * 0.235
            fw, fh = int(w * 0.17), int(h * 0.30)
            _flag(draw, x + int(w * fx), y + int(h * 0.30), fw, fh, kind)
            draw.line([x + int(w * (fx + 0.085)), y + int(h * 0.30),
                       x + int(w * (fx + 0.085)), y + int(h * 0.72)],
                      fill=INK, width=2)
        draw.rectangle([x + int(w * 0.05), y + int(h * 0.72),
                        x + int(w * 0.95), y + int(h * 0.88)], fill=(122, 82, 42))
        draw.rectangle([x + int(w * 0.05), y + int(h * 0.72),
                        x + int(w * 0.95), y + int(h * 0.78)], fill=(150, 105, 60))
    elif n == 4:  # Ebola: clinic tent + virus + count
        draw.rectangle([x, y, x + w, y + h], fill=(238, 230, 208))
        cx, cy = x + int(w * 0.20), y + int(h * 0.50)
        r = int(min(w, h) * 0.24)
        for a in range(0, 360, 30):
            dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
            draw.line([cx, cy, cx + dx * r * 1.5, cy + dy * r * 1.5], fill=RED, width=3)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        draw.ellipse([cx - int(r * 0.4), cy - int(r * 0.4),
                      cx + int(r * 0.2), cy + int(r * 0.2)], fill=(255, 122, 102))
        # clinic tent with red cross
        tx = x + int(w * 0.52)
        draw.polygon([(tx, y + int(h * 0.22)), (tx + int(w * 0.40), y + int(h * 0.22)),
                      (tx + int(w * 0.34), y + int(h * 0.85)),
                      (tx + int(w * 0.06), y + int(h * 0.85))], fill=(255, 255, 255),
                     outline=INK)
        draw.rectangle([tx + int(w * 0.17), y + int(h * 0.38),
                        tx + int(w * 0.23), y + int(h * 0.58)], fill=RED)
        draw.rectangle([tx + int(w * 0.13), y + int(h * 0.45),
                        tx + int(w * 0.27), y + int(h * 0.51)], fill=RED)
    elif n == 5:  # COP31: globe + wind turbine + thermometer
        sky(draw, x, y, w, h, (198, 228, 240), (220, 235, 225))
        cx, cy = x + int(w * 0.20), y + int(h * 0.50)
        r = int(min(w, h) * 0.26)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(92, 162, 212))
        draw.ellipse([cx - int(r * 0.5), cy - int(r * 0.7),
                      cx + int(r * 0.3), cy - int(r * 0.1)], fill=(62, 172, 82))
        draw.ellipse([cx - int(r * 0.2), cy + int(r * 0.2),
                      cx + int(r * 0.6), cy + int(r * 0.7)], fill=(62, 172, 82))
        # wind turbine
        tx = x + int(w * 0.52)
        draw.line([tx, y + int(h * 0.30), tx, y + int(h * 0.88)], fill=(255, 255, 255), width=3)
        for ang in (90, 210, 330):
            dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            draw.line([tx, y + int(h * 0.30),
                       tx + dx * int(h * 0.28), y + int(h * 0.30) + dy * int(h * 0.28)],
                      fill=(255, 255, 255), width=3)
        draw.ellipse([tx - 3, y + int(h * 0.30) - 3, tx + 3, y + int(h * 0.30) + 3],
                     fill=INK)
        # thermometer
        draw.rectangle([x + int(w * 0.78), y + int(h * 0.22),
                        x + int(w * 0.84), y + int(h * 0.78)], outline=RED, width=2)
        draw.ellipse([x + int(w * 0.75), y + int(h * 0.68),
                      x + int(w * 0.87), y + int(h * 0.90)], fill=RED)
    elif n == 6:  # Measles: virus + vaccine bottles + shield
        draw.rectangle([x, y, x + w, y + h], fill=(250, 246, 236))
        cx, cy = x + int(w * 0.18), y + int(h * 0.50)
        r = int(min(w, h) * 0.22)
        for a in range(0, 360, 30):
            dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
            draw.line([cx, cy, cx + dx * r * 1.5, cy + dy * r * 1.5], fill=RED, width=3)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        # vaccine bottles
        for i, bx in enumerate((0.44, 0.62, 0.80)):
            draw.rectangle([x + int(w * bx), y + int(h * 0.30),
                            x + int(w * (bx + 0.10)), y + int(h * 0.82)],
                           fill=(255, 255, 255), outline=NAVY)
            draw.rectangle([x + int(w * (bx + 0.03)), y + int(h * 0.20),
                            x + int(w * (bx + 0.07)), y + int(h * 0.30)], fill=NAVY)
            draw.rectangle([x + int(w * (bx + 0.01)), y + int(h * 0.45),
                            x + int(w * (bx + 0.09)), y + int(h * 0.62)],
                           fill=(62, 172, 82) if i % 2 == 0 else (255, 220, 0))
        lab = font(SANS_B, 9 if h < 60 else 11)
        draw.text((x + int(w * 0.40), y + int(h * 0.06)), "5,412 CASES",
                  font=lab, fill=RED)
    elif n == 7:  # Nvidia: chip + rising chart
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
    elif n == 8:  # Gaza: tents, aid truck, sun
        sky(draw, x, y, w, h, (250, 226, 180), (238, 210, 170))
        draw.ellipse([x + int(w * 0.80), y + int(h * 0.04),
                      x + int(w * 0.96), y + int(h * 0.34)], fill=(250, 172, 62))
        draw.rectangle([x, y + int(h * 0.72), x + w, y + h], fill=(196, 168, 120))
        for i, tx in enumerate((0.06, 0.30, 0.54)):
            draw.polygon([(x + int(w * tx), y + int(h * 0.72)),
                          (x + int(w * (tx + 0.11)), y + int(h * 0.42)),
                          (x + int(w * (tx + 0.22)), y + int(h * 0.72))],
                         fill=(255, 255, 255), outline=INK)
            draw.rectangle([x + int(w * (tx + 0.09)), y + int(h * 0.62),
                            x + int(w * (tx + 0.13)), y + int(h * 0.72)], fill=INK)
        # aid truck
        draw.rectangle([x + int(w * 0.72), y + int(h * 0.55),
                        x + int(w * 0.94), y + int(h * 0.80)], fill=(200, 200, 200), outline=INK)
        draw.rectangle([x + int(w * 0.88), y + int(h * 0.45),
                        x + int(w * 0.97), y + int(h * 0.62)], fill=(176, 58, 46))
        for wx in (0.78, 0.90):
            draw.ellipse([x + int(w * (wx - 0.03)), y + int(h * 0.78),
                          x + int(w * (wx + 0.03)), y + int(h * 0.92)], fill=INK)
        cap = font(SANS_B, 9 if h < 60 else 11)
        draw.text((x + int(w * 0.04), y + int(h * 0.06)), "1.4M FACE ACUTE HUNGER",
                  font=cap, fill=RED)
    elif n == 9:  # Mongolia: parliament building + $25M graft claim
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
                  font=font(SANS_B, 15 if h < 60 else 22), fill=RED)
        draw.text((x + int(w * 0.62), y + int(h * 0.55)), "GRAFT CLAIM",
                  font=font(SANS_B, 9), fill=RED)
    elif n == 10:  # Serbia: hemicycle of seats + ballot box, 140/250
        draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 248))
        cx, cy = x + int(w * 0.42), y + int(h * 0.95)
        for ring, rr in ((0.42, 0.30), (0.30, 0.22)):
            for k in range(7):
                ang = math.radians(200 + k * 20)
                sx = cx + math.cos(ang) * int(w * rr * 1.4)
                sy = cy + math.sin(ang) * int(h * rr * 1.4)
                draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3],
                             fill=(46, 125, 50) if k < 5 else (31, 78, 121))
        draw.rectangle([x + int(w * 0.70), y + int(h * 0.30),
                        x + int(w * 0.92), y + int(h * 0.78)], fill=(200, 40, 40), outline=INK)
        draw.rectangle([x + int(w * 0.70), y + int(h * 0.30),
                        x + int(w * 0.92), y + int(h * 0.42)], fill=(255, 255, 255), outline=INK)
        draw.rectangle([x + int(w * 0.78), y + int(h * 0.22),
                        x + int(w * 0.84), y + int(h * 0.34)], fill=(255, 255, 255), outline=INK)
        lab = font(SANS_B, 11 if h < 60 else 14)
        draw.text((x + int(w * 0.04), y + int(h * 0.06)), "140 / 250",
                  font=lab, fill=NAVY)
    elif n == 11:  # Bangladesh: factory, sawtooth roof, shirts on a line
        sky(draw, x, y, w, h, (198, 228, 240), (220, 230, 220))
        draw.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(150, 140, 120))
        draw.rectangle([x + int(w * 0.08), y + int(h * 0.40),
                        x + int(w * 0.62), y + int(h * 0.92)], fill=(176, 58, 46))
        for sx in (0.10, 0.22, 0.34, 0.46):
            draw.polygon([(x + int(w * sx), y + int(h * 0.40)),
                          (x + int(w * (sx + 0.06)), y + int(h * 0.28)),
                          (x + int(w * (sx + 0.12)), y + int(h * 0.40))],
                         fill=(140, 40, 30))
        draw.rectangle([x + int(w * 0.66), y + int(h * 0.30),
                        x + int(w * 0.72), y + int(h * 0.92)], fill=(90, 80, 70))
        for cx, cy, r in [(0.69, 0.18, 0.04), (0.74, 0.10, 0.03)]:
            draw.ellipse([x + int(w * (cx - r)), y + int(h * (cy - r)),
                          x + int(w * (cx + r)), y + int(h * (cy + r))], fill=(120, 120, 120))
        # shirts on a line
        draw.line([x + int(w * 0.70), y + int(h * 0.14),
                   x + int(w * 0.98), y + int(h * 0.10)], fill=INK, width=2)
        for sx, col in [(0.74, (255, 220, 0)), (0.84, (62, 172, 82)), (0.93, (92, 162, 212))]:
            draw.rectangle([x + int(w * (sx - 0.03)), y + int(h * 0.13),
                            x + int(w * (sx + 0.03)), y + int(h * 0.32)], fill=col, outline=INK)
        cap = font(SANS_B, 9 if h < 60 else 11)
        draw.text((x + int(w * 0.04), y + int(h * 0.04)), "TK 30,000 MINIMUM",
                  font=cap, fill=RED)
    elif n == 12:  # An-12: plane diving, smoke plume, mountains
        sky(draw, x, y, w, h, (170, 190, 210), (210, 220, 225))
        draw.polygon([(x, y + h), (x + int(w * 0.30), y + int(h * 0.45)),
                      (x + int(w * 0.55), y + h)], fill=(120, 130, 140))
        draw.polygon([(x + int(w * 0.45), y + h), (x + int(w * 0.75), y + int(h * 0.55)),
                      (x + w, y + h)], fill=(100, 110, 120))
        for cx, cy, r in [(0.72, 0.30, 0.06), (0.80, 0.38, 0.045), (0.66, 0.38, 0.035)]:
            rx, ry = int(w * r), int(h * r)
            draw.ellipse([x + int(w * cx) - rx, y + int(h * cy) - ry,
                          x + int(w * cx) + rx, y + int(h * cy) + ry], fill=(90, 90, 90))
        # diving plane silhouette
        px, py = x + int(w * 0.38), y + int(h * 0.30)
        draw.polygon([(px - int(w * 0.20), py + int(h * 0.06)),
                      (px + int(w * 0.22), py - int(h * 0.06)),
                      (px + int(w * 0.26), py - int(h * 0.02)),
                      (px - int(w * 0.16), py + int(h * 0.12))], fill=INK)
        draw.polygon([(px, py - int(h * 0.02)),
                      (px + int(w * 0.10), py - int(h * 0.22)),
                      (px + int(w * 0.14), py - int(h * 0.18)),
                      (px + int(w * 0.04), py + int(h * 0.02))], fill=INK)
        draw.polygon([(px - int(w * 0.10), py + int(h * 0.08)),
                      (px - int(w * 0.06), py + int(h * 0.24)),
                      (px - int(w * 0.02), py + int(h * 0.22)),
                      (px - int(w * 0.04), py + int(h * 0.10))], fill=INK)
    else:  # 13 Mozambique: courthouse columns + gavel + 5 charges
        draw.rectangle([x, y, x + w, y + h], fill=(238, 230, 208))
        lab = font(SANS_B, 10 if h < 60 else 12)
        tw = draw.textlength("5 CHARGES", font=lab)
        draw.text((x + (w - tw) / 2, y + 1), "5 CHARGES",
                  font=lab, fill=RED)
        draw.polygon([(x + int(w * 0.10), y + int(h * 0.34)),
                      (x + int(w * 0.50), y + int(h * 0.14)),
                      (x + int(w * 0.90), y + int(h * 0.34))], fill=NAVY)
        for cx in (0.18, 0.38, 0.58, 0.78):
            draw.rectangle([x + int(w * (cx - 0.04)), y + int(h * 0.36),
                            x + int(w * (cx + 0.04)), y + int(h * 0.85)], fill=(240, 222, 172),
                           outline=NAVY)
        draw.rectangle([x + int(w * 0.06), y + int(h * 0.85),
                        x + int(w * 0.94), y + int(h * 0.92)], fill=NAVY)
        # gavel
        draw.line([x + int(w * 0.55), y + int(h * 0.55),
                   x + int(w * 0.85), y + int(h * 0.35)], fill=(122, 82, 42), width=4)
        draw.rectangle([x + int(w * 0.78), y + int(h * 0.28),
                        x + int(w * 0.92), y + int(h * 0.42)], fill=(122, 82, 42))


# ---------------------------------------------------------------- panels
def draw_panel(draw, entry, x, y, w, h, lead):
    n, region, tag, headline, deck, _lon, _lat = entry
    col = REGION_COLOUR[region]
    art_h = 92 if lead else 44
    draw.rectangle([x, y, x + w, y + h], fill=PAPER, outline=bp.PANEL_LINE)
    paint(draw, n, x + 1, y + 1, w - 2, art_h - 1)
    draw.line([x, y + art_h, x + w, y + art_h], fill=col, width=3)
    badge(draw, x + w - 20, y + art_h, n, col)
    ty = y + art_h + 8
    tag_size = 10 if lead else 9
    draw.text((x + 8, ty), region + " \u00b7 " + tag,
              font=font(SANS_B, tag_size), fill=col)
    head_size = 17 if lead else 13
    deck_size = 11 if lead else 9
    head_lines = balance_two(draw, headline, font(SERIF_B, head_size), w - 16)
    if head_lines is None:
        head_lines = fit_lines(draw, headline, font(SERIF_B, head_size), w - 16, 2)
    y2 = text_block(draw, x + 8, ty + tag_size + 6, head_lines,
                    font(SERIF_B, head_size), INK, head_size + 3)
    deck_lines = fit_lines(draw, deck, font(SANS, deck_size), w - 16, 2)
    text_block(draw, x + 8, y2 + 2, deck_lines,
               font(SANS, deck_size), (70, 65, 55), deck_size + 3)


def centred(draw, cx, y, text, fnt, fill):
    tw = draw.textlength(text, font=fnt)
    draw.text((cx - tw / 2, y), text, font=fnt, fill=fill)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # Masthead: cream paper, red kicker, giant black serif date.
    d.text((16, 8), "THE WORLD\u2019S NEWS IN ONE PICTURE",
           font=font(SANS_B, 12), fill=RED)
    right_kick = "43 STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM TUESDAY"
    d.text((W - 16 - d.textlength(right_kick, font=font(SANS_B, 12)), 8),
           right_kick, font=font(SANS_B, 12), fill=INK)
    d.text((16, 28), "Tuesday 17 November 2026",
           font=font(SERIF_B, 56), fill=INK)
    d.line([16, 100, W - 16, 100], fill=INK, width=2)
    # Lead row (3 tall panels) + two rows of 5.
    xs3 = [16, 349, 682]
    for i, x in enumerate(xs3):
        draw_panel(d, MAINS[i], x, 108, 326, 196, lead=True)
    xs5 = [16, 216, 416, 616, 816]
    k = 3
    for x in xs5:
        draw_panel(d, MAINS[k], x, 312, 192, 150, lead=False)
        k += 1
    for x in xs5:
        draw_panel(d, MAINS[k], x, 470, 192, 150, lead=False)
        k += 1
    # Bottom: map left, also-on list right, legend under the map.
    d.text((16, 632), "WHERE IT HAPPENED", font=font(SANS_B, 14), fill=NAVY)
    d.text((466, 632), "ALSO ON TUESDAY 17 NOVEMBER",
           font=font(SANS_B, 14), fill=NAVY)
    d.line([16, 652, 1008, 652], fill=GOLD, width=2)
    bp.MAINS = MAINS
    bp.ALSO = ALSO
    bp.draw_map(d, 16, 660, 430, 280)
    lx = 16
    for name, col in LEGEND:
        d.ellipse([lx, 948, lx + 9, 957], fill=col)
        d.text((lx + 13, 946), name, font=font(SANS, 10), fill=INK)
        lx += 13 + d.textlength(name, font=font(SANS, 10)) + 14
    for i, (num, txt, _lon, _lat) in enumerate(ALSO):
        col_x = 466 if i < 15 else 746
        row_y = 662 + (i % 15) * 19
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
    centred(d, W / 2, 972,
            "Every story here happened or was first reported on Tuesday 17 November 2026; contested claims are marked as claims.",
            font(SERIF, 11), MUTED)
    centred(d, W / 2, 990,
            "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN. Original drawings.",
            font(SERIF, 11), MUTED)
    img.save("entry_v3.png")


if __name__ == "__main__":
    build()
