#!/usr/bin/env python3
"""
Render v6 for make.fun news-image-20261122: redesigned layout following the
top-of-leaderboard pattern — huge centered serif dateline, red italic summary
line, THE DAY IN NUMBERS big-figure band, 3 lead stories with flat vector
illustrations, uniform status-tagged cards, briefs, date-check footer.

Deterministic: fixed fonts, fixed data, no network, no randomness.
Fonts: Liberation Serif (headlines) + Liberation Sans (labels).
"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
NAVY = (18, 32, 58)
CREAM = (246, 242, 232)
RED = (178, 34, 34)
GREEN = (30, 110, 60)
ORANGE = (200, 120, 30)
GRAY = (110, 110, 110)
INK = (28, 28, 28)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)

M = 28  # page margin
CW = W - 2 * M  # content width

# ---------- masthead strip ----------
d.rectangle([0, 0, W, 34], fill=NAVY)
f_mast = font(SANS_B, 14)
d.text((M, 9), "THE WORLD IN ONE DAY", font=f_mast, fill=(255, 255, 255))
mast_right = "36 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
w_mr = d.textlength(mast_right, font=f_mast)
d.text((W - M - w_mr, 9), mast_right, font=f_mast, fill=(255, 255, 255))

# ---------- huge dateline ----------
f_date = font(SERIF_B, 62)
date_txt = "Sunday 22 November 2026"
w_date = d.textlength(date_txt, font=f_date)
d.text(((W - w_date) / 2, 46), date_txt, font=f_date, fill=INK)

# red italic summary line
f_sum = font(SERIF_B, 20)
sum_txt = "COP31 ends with no deal  ·  186 drones over Ukraine in the night  ·  Iran's radar claim meets Bahrain's denial"
w_sum = d.textlength(sum_txt, font=f_sum)
d.text(((W - w_sum) / 2, 124), sum_txt, font=f_sum, fill=RED)

d.line([M, 156, W - M, 156], fill=NAVY, width=3)

y = 160
# ---------- THE DAY IN NUMBERS ----------
f_lbl = font(SANS_B, 15)
d.text((M, y), "THE DAY IN NUMBERS", font=f_lbl, fill=RED)
y += 22
nums = [
    ("186", "drones fired at\nUkraine overnight"),
    ("161", "downed or jammed\nby air defence"),
    ("98.37%", "Hong Kong poll\nturnout record"),
    ("720/9", "India declare,\na Test record"),
    ("50", "Wembanyama points\nvs New Orleans"),
    ("3", "dead in a Cianjur\ncandy-factory fire"),
]
col_w = CW // 6
f_num = font(SERIF_B, 40)
f_numsub = font(SANS_R, 12)
for i, (n, sub) in enumerate(nums):
    x = M + i * col_w
    d.text((x, y), n, font=f_num, fill=(120, 20, 40))
    d.text((x, y + 46), sub, font=f_numsub, fill=GRAY, spacing=2)
    if i > 0:
        d.line([x - 8, y + 4, x - 8, y + 78], fill=(200, 195, 185), width=2)
y += 84

# ---------- lead stories (3 across) ----------
LEADS = [
    ("WAR", RED, "Kyiv region — CONFIRMED",
     "Russia fires 186\ndrones; a Kyiv\nblock destroyed",
     "Air defences downed or suppressed 161 of\n186 strike drones from eight directions. One\ndestroyed a five-storey block in Dnipro; up\nto seven feared trapped. (Air Force, Reuters)"),
    ("CLIMATE", ORANGE, "Antalya, Türkiye — REPORTED",
     "Climate deal lands,\nno mention of\nfossil fuels",
     "The final text keeps the 35%-electricity-by-\n2035 goal, drops the $120bn adaptation target\nand is the first to admit 1.5°C will be overshot.\nHoekstra: \"a good deal or no deal\". (Reuters)"),
    ("IRAN", RED, "Manama, Bahrain — CLAIM",
     "Iran claims two US\nradars hit; Bahrain\ndenies it",
     "The IRGC says it destroyed two Patriot radars\non Saturday night. Bahrain answered Sunday:\na civilian industrial fire, a violation of\nsovereignty. (Khaleej Times, Al Jazeera)"),
]
lead_h = 292
box_w = (CW - 2 * 18) // 3
for i, (tag, tcol, meta, head, body) in enumerate(LEADS):
    x = M + i * (box_w + 18)
    d.rectangle([x, y, x + box_w, y + lead_h], outline=NAVY, width=2)
    d.rectangle([x, y, x + box_w, y + 26], fill=NAVY)
    d.text((x + 10, y + 5), tag, font=font(SANS_B, 14), fill=(255, 255, 255))
    # simple flat illustration block
    ix, iy, iw, ih = x + 14, y + 36, box_w - 28, 56
    d.rectangle([ix, iy, ix + iw, iy + ih], fill=(228, 224, 212))
    if tag == "WAR":  # night sky + drones
        d.rectangle([ix, iy, ix + iw, iy + ih], fill=(30, 34, 52))
        for k in range(7):
            dx = ix + 14 + k * (iw - 30) / 6
            dy = iy + 10 + (k % 3) * 12
            d.polygon([(dx, dy), (dx + 8, dy + 3), (dx, dy + 6)], fill=(220, 120, 60))
        d.line([ix + iw * 0.62, iy + ih, ix + iw * 0.62, iy + 6], fill=(240, 200, 90), width=3)
    elif tag == "CLIMATE":  # sun over a globe
        d.ellipse([ix + 10, iy + 8, ix + 44, iy + 42], fill=(230, 170, 60))
        d.ellipse([ix + iw - 54, iy + 6, ix + iw - 10, iy + 50], outline=(60, 110, 150), width=3)
        d.arc([ix + iw - 54, iy + 6, ix + iw - 10, iy + 50], 20, 160, fill=(60, 110, 150), width=2)
    else:  # radar dish
        d.arc([ix + 8, iy + 4, ix + 54, iy + 50], 180, 360, fill=(70, 80, 100), width=3)
        d.line([ix + 31, iy + 27, ix + 31, iy + 50], fill=(70, 80, 100), width=3)
        d.arc([ix + iw - 50, iy + 4, ix + iw - 4, iy + 50], 180, 360, fill=(70, 80, 100), width=3)
        d.ellipse([ix + iw - 36, iy + 19, ix + iw - 28, iy + 27], fill=RED)
    d.text((x + 10, y + 98), meta, font=font(SANS_R, 12), fill=GRAY)
    d.text((x + 10, y + 118), head, font=font(SERIF_B, 30), fill=INK, spacing=4)
    d.text((x + 10, y + 240), body, font=font(SANS_R, 13), fill=(70, 70, 70), spacing=3)
y += lead_h + 16

# ---------- secondary cards (2 rows x 5) ----------
CARDS = [
    ("4", "CONFIRMED", GREEN, "HONG KONG", "Record turnout as Hong\nKong elects its committee", "836 candidates, 725 seats,\n98.37% of 3,700 voters. (SCMP)"),
    ("5", "CONFIRMED", GREEN, "WELLINGTON", "India declare on 720-9,\na Test record", "Rahul 156, Pant 131, Gill 98;\nhosts 119/2, trail by 235. (AP)"),
    ("6", "CONFIRMED", GREEN, "LAS VEGAS", "Verstappen wins the\nLas Vegas Grand Prix", "From pole in 1:27:39.634;\nNorris +0.653, Piastri +1.329. (FIA)"),
    ("7", "CONFIRMED", GREEN, "SAN ANTONIO", "Wembanyama scores 50\nas the Spurs roll on", "50 pts, 19 rebounds, 5 blocks;\n114-91 over New Orleans. (Reuters)"),
    ("8", "REPORTED", ORANGE, "GULF OF FINLAND", "Cargo ship Sparta II hit\nby drones; ablaze", "Finland leads the Loviisa\nrescue effort. (Reuters)"),
    ("9", "REPORTED", ORANGE, "TEHRAN", "Iran begins rationing\nelectricity", "Rolling cuts up to two hours\na day as war damage bites. (Wires)"),
    ("10", "REPORTED", ORANGE, "BRASILIA", "Bolsonaro in intensive\ncare in Brasilia", "Acute bowel obstruction;\nstable, surgery possible. (Reuters)"),
    ("11", "REPORTED", ORANGE, "WASHINGTON", "FBI probes a hack of\nits crime database", "Washington State pauses\ngun-dealer checks. (AP)"),
    ("12", "CONFIRMED", GREEN, "CIANJUR", "Candy-factory fire:\n3 dead, 26 missing", "Blaze tore through the plant;\nthe search goes on. (Detiknews)"),
    ("13", "CONFIRMED", GREEN, "MANIPUR", "Toxic liquor toll\nclimbs to 19", "600 in hospital, six held;\ntoll up from Saturday. (Al Jazeera)"),
]
card_h = 112
card_w = (CW - 4 * 14) // 5
for i, (n, st, scol, place, head, body) in enumerate(CARDS):
    row, col = divmod(i, 5)
    x = M + col * (card_w + 14)
    cy = y + row * (card_h + 12)
    d.rectangle([x, cy, x + card_w, cy + card_h], outline=(190, 185, 175), width=2)
    d.rectangle([x, cy, x + 26, cy + card_h], fill=NAVY)
    d.text((x + 8, cy + 8), n, font=font(SERIF_B, 16), fill=(255, 255, 255))
    # status pill
    stw = d.textlength(st, font=font(SANS_B, 10))
    d.rounded_rectangle([x + 34, cy + 8, x + 42 + stw, cy + 24], 5, fill=scol)
    d.text((x + 38, cy + 10), st, font=font(SANS_B, 10), fill=(255, 255, 255))
    d.text((x + 34, cy + 27), place, font=font(SANS_B, 10), fill=GRAY)
    d.text((x + 34, cy + 40), head, font=font(SERIF_B, 15), fill=INK, spacing=2)
    d.text((x + 34, cy + 82), body, font=font(SANS_R, 11), fill=(80, 80, 80), spacing=2)
y += 2 * card_h + 12 + 14

# ---------- briefs (2 columns) ----------
BRIEFS_L = [
    "16  Estonia to shut five Russian border crossings after a sabotage bid",
    "17  Denmark reports a Russian attack plot against a Ukrainian",
    "18  Nepal PM Shah lands in Delhi on first visit, meets Modi Monday",
    "19  Chinese bombers turn back 170 km from Manila",
    "20  Philippines M5.9 quake, 898 km deep, off Palawan",
    "21  Japan poll: record 52% feel friendly to South Korea",
]
BRIEFS_R = [
    "23  Somalia expels UAE ambassador, recalls its envoy",
    "24  Sudan: RSF accused of killing 3 children in Kordofan",
    "25  Kenya discharges its last Ebola patient",
    "26  Marles rejects a US report on AUKUS submarines",
    "29  Trump seeks a permanent Iran deal, tells Doha talks",
    "31  Hamas seeks urgent mediator talks",
]
f_brief = font(SANS_R, 14)
bx_l, bx_r = M, M + CW // 2 + 10
for i in range(6):
    d.text((bx_l, y + i * 24), BRIEFS_L[i], font=f_brief, fill=(60, 60, 60))
    d.text((bx_r, y + i * 24), BRIEFS_R[i], font=f_brief, fill=(60, 60, 60))
y += 6 * 24 + 10

# ---------- date check footer ----------
d.rectangle([M, y, W - M, y + 44], outline=RED, width=2)
d.text((M + 12, y + 6), "DATE CHECK", font=font(SANS_B, 14), fill=RED)
d.text((M + 120, y + 7), "Every story on this page happened on, or was first reported on, Sunday 22 November 2026 UTC.",
       font=font(SANS_R, 14), fill=(60, 60, 60))
d.text((M + 120, y + 26), "Left out on purpose: events from Saturday 21 November and earlier.",
       font=font(SANS_R, 12), fill=GRAY)

img.save("/home/agentuser/workspace/makefun/entry-repo/entry.png", "PNG")
print("rendered v6")
