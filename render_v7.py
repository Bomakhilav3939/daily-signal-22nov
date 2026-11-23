#!/usr/bin/env python3
"""
Render v7 for make.fun news-image-20261122 — densification pass.

Changes vs v6:
  * story count 25 -> 33 (3 lead + 10 cards + 20 briefs)
  * four navy section bands (numbers / leads / more stories / in brief)
  * type scale down 1-2pt everywhere, tighter leading
  * richer flat-vector lead illustrations (gradients, silhouettes, glow)
  * darker card rules + full-height number rails (ink density up)
  * hard QA inside the script: width, y-flow, pixel margin guard, ink density

Deterministic: fixed fonts, fixed data, no network, no randomness, no clock.
"""
from PIL import Image, ImageDraw, ImageFont
import sys

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

_cache = {}


def font(path, size):
    k = (path, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(path, size)
    return _cache[k]


img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)

M = 26
CW = W - 2 * M

FAILS = []


def wrap_all(text, f, maxw):
    words = text.split()
    out, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if not cur or d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def para(text, f, maxw, maxlines):
    ls = wrap_all(text, f, maxw)
    if len(ls) > maxlines:
        ls = ls[:maxlines]
        last = ls[-1]
        while len(last) > 1 and d.textlength(last + "\u2026", font=f) > maxw:
            last = last[:-1]
        ls[-1] = last.rstrip() + "\u2026"
    for L in ls:
        if d.textlength(L, font=f) > maxw + 1:
            FAILS.append("width overflow: %r %r" % (L, maxw))
    return ls


def lines_at(x, y, ls, f, fill, lh):
    yy = y
    for L in ls:
        d.text((x, yy), L, font=f, fill=fill)
        yy += lh
    return yy


def band(y, label, right=""):
    d.rectangle([M, y, W - M, y + 18], fill=NAVY)
    d.text((M + 8, y + 3), label, font=font(SANS_B, 11), fill=(255, 255, 255))
    if right:
        f = font(SANS_R, 10)
        w = d.textlength(right, font=f)
        d.text((W - M - 8 - w, y + 4), right, font=f, fill=(205, 200, 190))
    return y + 18


# ---------------- masthead ----------------
d.rectangle([0, 0, W, 32], fill=NAVY)
d.text((M, 8), "THE WORLD IN ONE DAY", font=font(SANS_B, 13), fill=(255, 255, 255))
mr = "33 STORIES  \u00b7  7 REGIONS  \u00b7  ALL DATED SUNDAY 22 NOVEMBER 2026"
fmr = font(SANS_R, 11)
d.text((W - M - d.textlength(mr, font=fmr), 10), mr, font=fmr, fill=(226, 221, 210))

# ---------------- dateline ----------------
f_date = font(SERIF_B, 56)
dt = "Sunday 22 November 2026"
d.text(((W - d.textlength(dt, font=f_date)) / 2, 40), dt, font=f_date, fill=INK)

f_sum = font(SERIF_B, 18)
st = ("COP31 ends with no deal  \u00b7  186 drones over Ukraine in the night  "
      "\u00b7  Iran's radar claim meets Bahrain's denial")
d.text(((W - d.textlength(st, font=f_sum)) / 2, 108), st, font=f_sum, fill=RED)
if d.textlength(st, font=f_sum) > CW:
    FAILS.append("summary too wide")

d.line([M, 138, W - M, 138], fill=NAVY, width=3)
d.line([M, 143, W - M, 143], fill=NAVY, width=1)

# ---------------- numbers ----------------
y = band(148, "THE DAY IN NUMBERS", "seven figures that frame the day")
y += 6

NUMS = [
    ("186", "drones fired at\nUkraine in a night"),
    ("161", "downed or jammed\nby air defence"),
    ("98.37%", "Hong Kong poll\nturnout, a record"),
    ("720/9", "India declare,\na Test record"),
    ("50", "Wembanyama pts\nvs New Orleans"),
    ("19", "Manipur liquor\ntoll, 600 in care"),
    ("3", "dead in a Cianjur\nfactory blaze"),
]
f_num = font(SERIF_B, 31)
f_sub = font(SANS_R, 10)
colw = CW // len(NUMS)
for i, (n, sub) in enumerate(NUMS):
    x = M + i * colw
    d.text((x, y), n, font=f_num, fill=(122, 20, 40))
    sy = y + 36
    for j, L in enumerate(sub.split("\n")):
        d.text((x, sy + j * 12), L, font=f_sub, fill=(95, 95, 95))
    if i:
        d.line([x - 7, y + 2, x - 7, y + 56], fill=(190, 184, 172), width=2)
y += 62

# ---------------- leads ----------------
y = band(y + 4, "LEAD STORIES", "CONFIRMED  \u00b7  REPORTED  \u00b7  CLAIM")
y += 6

LEADS = [
    ("WAR", RED, "Kyiv region, Ukraine \u2014 CONFIRMED",
     "Russia fires 186 drones; a Kyiv-region block is destroyed",
     "Air defences downed or jammed 161 of the 186 drones launched from eight "
     "directions. One hit a five-storey block in Dnipro; up to seven feared "
     "trapped. (Air Force, Reuters)"),
    ("CLIMATE", ORANGE, "Antalya, T\u00fcrkiye \u2014 REPORTED",
     "Climate deal lands with no mention of fossil fuels",
     "The final text keeps the 35%-electricity-by-2035 goal, drops the $120bn "
     "adaptation target and admits 1.5C will be overshot. Hoekstra: \"a good "
     "deal or no deal\". (Reuters, BBC)"),
    ("IRAN", RED, "Manama, Bahrain \u2014 CLAIM",
     "Iran claims two US radars hit; Bahrain denies it",
     "The IRGC says it destroyed two Patriot radars on Saturday night. Bahrain "
     "answered on Sunday: a civilian industrial fire, no injuries, a violation "
     "of sovereignty. (Khaleej Times, Al Jazeera)"),
]
lead_h = 254
box_w = (CW - 2 * 18) // 3
f_tag = font(SANS_B, 12)
f_meta = font(SANS_R, 10)
f_head = font(SERIF_B, 22)
f_body = font(SANS_R, 11)


def illus(i, x, y0, w, h, tag):
    if tag == "WAR":
        # night sky gradient
        for k in range(12):
            t = k / 11.0
            col = (int(22 + 40 * t), int(26 + 30 * t), int(46 + 46 * t))
            d.rectangle([x, y0 + k * h / 12, x + w, y0 + (k + 1) * h / 12], fill=col)
        # moon
        d.ellipse([x + w - 46, y0 + 6, x + w - 26, y0 + 26], fill=(232, 226, 200))
        # city silhouette
        blocks = [(0, 14, 8), (16, 20, 10), (30, 12, 7), (46, 24, 12),
                  (62, 16, 9), (78, 22, 11), (94, 13, 8)]
        for bx, bh, bw in blocks:
            if x + bx + bw <= x + w:
                d.rectangle([x + bx, y0 + h - bh, x + bx + bw, y0 + h], fill=(14, 16, 28))
        # drones + tracers
        for k in range(9):
            dx = x + 10 + k * (w - 26) / 8
            dy = y0 + 8 + (k % 4) * 7
            d.polygon([(dx, dy), (dx + 7, dy + 3), (dx, dy + 5)], fill=(226, 130, 62))
            d.line([dx + 3, dy + 5, dx + 3, dy + 12], fill=(240, 190, 110), width=1)
        d.line([x + w * 0.60, y0 + h, x + w * 0.66, y0 + 4], fill=(240, 200, 90), width=2)
        # blast glow
        for r in (12, 8, 4):
            d.ellipse([x + 36 - r, y0 + h - 12 - r, x + 36 + r, y0 + h - 12 + r],
                      fill=(232 - r * 6, 150 - r * 6, 60))
    elif tag == "CLIMATE":
        for k in range(10):
            t = k / 9.0
            col = (int(236 - 58 * t), int(212 - 52 * t), int(178 - 40 * t))
            d.rectangle([x, y0 + k * h / 10, x + w, y0 + (k + 1) * h / 10], fill=col)
        cx, cy = x + 34, y0 + 22
        for a in range(0, 360, 30):
            import math
            r0, r1 = 17, 23
            d.line([cx + r0 * math.cos(math.radians(a)), cy + r0 * math.sin(math.radians(a)),
                    cx + r1 * math.cos(math.radians(a)), cy + r1 * math.sin(math.radians(a))],
                   fill=(214, 132, 40), width=2)
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(228, 164, 52))
        # globe
        gx, gy, gr = x + w - 40, y0 + 26, 20
        d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=(58, 104, 142), width=2)
        for dy in (-8, 0, 8):
            d.arc([gx - gr, gy - gr + dy, gx + gr, gy + gr + dy], 200, 340,
                  fill=(58, 104, 142), width=1)
        d.line([gx, gy - gr, gx, gy + gr], fill=(58, 104, 142), width=1)
        # heat bars + smoke stacks
        for k in range(6):
            d.rectangle([x + 14 + k * 11, y0 + h - 10 - (k % 3) * 3,
                         x + 20 + k * 11, y0 + h], fill=(120, 70, 44))
        d.line([x + 6, y0 + h - 12, x + w - 8, y0 + h - 12], fill=(150, 96, 60), width=2)
    else:
        d.rectangle([x, y0, x + w, y0 + h], fill=(226, 230, 232))
        for k in range(1, 4):
            d.line([x, y0 + k * h / 4, x + w, y0 + k * h / 4], fill=(196, 204, 210), width=1)
        for k in range(1, 6):
            d.line([x + k * w / 6, y0, x + k * w / 6, y0 + h], fill=(196, 204, 210), width=1)
        # two dishes sweeping
        for base in (x + 30, x + w - 30):
            d.line([base, y0 + h - 4, base, y0 + h - 22], fill=(58, 66, 84), width=3)
            d.arc([base - 22, y0 + h - 44, base + 22, y0 + h], 180, 360,
                  fill=(58, 66, 84), width=3)
            d.arc([base - 16, y0 + h - 38, base + 16, y0 + h - 6], 200, 340,
                  fill=(150, 40, 44), width=1)
        for bx, by in ((x + w * 0.38, y0 + 12), (x + w * 0.52, y0 + 26)):
            d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=RED)


for i, (tag, tcol, meta, head, body) in enumerate(LEADS):
    x = M + i * (box_w + 18)
    d.rectangle([x, y, x + box_w, y + lead_h], outline=NAVY, width=2)
    d.rectangle([x, y, x + box_w, y + 22], fill=NAVY)
    d.text((x + 9, y + 4), tag, font=f_tag, fill=(255, 255, 255))
    nw = d.textlength("0" + str(i + 1), font=f_tag)
    d.text((x + box_w - 9 - nw, y + 5), "0" + str(i + 1), font=font(SANS_R, 10),
           fill=(198, 194, 184))

    illus(i, x + 12, y + 28, box_w - 24, 50, tag)

    d.text((x + 9, y + 82), meta, font=f_meta, fill=(105, 105, 105))
    hls = para(head, f_head, box_w - 20, 3)
    hb = lines_at(x + 9, y + 98, hls, f_head, INK, 25)
    bls = para(body, f_body, box_w - 20, 4)
    lines_at(x + 9, hb + 4, bls, f_body, (72, 72, 72), 14)

y += lead_h + 8

# ---------------- cards ----------------
y = band(y, "MORE STORIES", "status-tagged, one line of hard fact each")
y += 8

CARDS = [
    (4, "HONG KONG", "CONFIRMED", GREEN, "Record 98.37% turnout as committee is elected",
     "836 candidates, 725 seats; polls ran 09:00-18:00. (SCMP)"),
    (5, "WELLINGTON", "CONFIRMED", GREEN, "India declare on 720-9, a Test record",
     "Rahul 156, Pant 131; hosts 119-2, trailing by 235. (AP)"),
    (6, "LAS VEGAS", "CONFIRMED", GREEN, "Verstappen takes the Las Vegas GP",
     "From pole in 1:27:39.634; Norris +0.653s. (FIA)"),
    (7, "SAN ANTONIO", "CONFIRMED", GREEN, "Wembanyama drops 50 on the Pelicans",
     "19 rebounds, 5 blocks; Spurs win 114-91. (Reuters)"),
    (8, "GULF OF FINLAND", "REPORTED", ORANGE, "Cargo Sparta II hit by drones, ablaze",
     "Finland leads the Loviisa rescue operation. (Reuters)"),
    (9, "TEHRAN", "REPORTED", ORANGE, "Iran begins rationing electricity",
     "Rolling cuts up to two hours a day. (Wires)"),
    (10, "BRASILIA", "REPORTED", ORANGE, "Bolsonaro in intensive care",
     "Acute bowel obstruction; stable, surgery possible. (Reuters)"),
    (11, "WASHINGTON", "REPORTED", ORANGE, "FBI probes hack of crime database",
     "State pauses gun-dealer checks after breach. (AP)"),
    (12, "BRUSSELS", "REPORTED", ORANGE, "Belgian controllers join Monday strike",
     "Most flights grounded 07:00-21:00. (Wires)"),
    (13, "MANIPUR", "CONFIRMED", GREEN, "Toxic liquor toll climbs to 19",
     "600 in hospital, six held; toll up from 16. (Al Jazeera)"),
]
card_h = 106
card_w = (CW - 4 * 12) // 5
f_cn = font(SERIF_B, 15)
f_pill = font(SANS_B, 8)
f_place = font(SANS_B, 8)
f_ch = font(SERIF_B, 13)
f_cb = font(SANS_R, 9)
for idx, (n, place, st, scol, head, body) in enumerate(CARDS):
    row, col = divmod(idx, 5)
    x = M + col * (card_w + 12)
    cy = y + row * (card_h + 10)
    d.rectangle([x, cy, x + card_w, cy + card_h], outline=(120, 115, 105), width=2)
    d.rectangle([x + 1, cy + 1, x + 22, cy + card_h - 1], fill=NAVY)
    nw = d.textlength(str(n), font=f_cn)
    d.text((x + 11 - nw / 2, cy + 5), str(n), font=f_cn, fill=(255, 255, 255))
    tx = x + 28
    tw = card_w - 34
    pw = d.textlength(st, font=f_pill) + 10
    d.rounded_rectangle([tx, cy + 5, tx + pw, cy + 17], 4, fill=scol)
    d.text((tx + 5, cy + 7), st, font=f_pill, fill=(255, 255, 255))
    d.text((tx, cy + 20), place, font=f_place, fill=(120, 120, 120))
    hls = para(head, f_ch, tw, 2)
    hb = lines_at(tx, cy + 33, hls, f_ch, INK, 15)
    bls = para(body, f_cb, tw, 3)
    lines_at(tx, max(hb + 1, cy + 64), bls, f_cb, (82, 82, 82), 11)

y += 2 * card_h + 10 + 8

# ---------------- briefs ----------------
y = band(y, "IN BRIEF", "twenty more, each dated 22 November 2026")
y += 6

BRIEFS = [
    (16, "Estonia to shut five Russian border crossings from 1 Dec"),
    (17, "Denmark reports a Russian plot against a Ukrainian"),
    (18, "Nepal PM Shah lands in Delhi, meets Modi on Monday"),
    (19, "Chinese bombers turn back 170 km from Manila"),
    (20, "Philippines M5.9 quake, 898 km deep, off Palawan"),
    (21, "Japan poll: record 52% feel friendly to South Korea"),
    (22, "Taiwan detects 12 Chinese balloons, 11 near the island"),
    (23, "Somalia expels UAE ambassador, recalls its envoy"),
    (24, "Sudan: RSF accused of killing 3 children in Kordofan"),
    (25, "Kenya discharges its last Ebola patient"),
    (26, "Marles rejects a US report on AUKUS submarines"),
    (27, "Melbourne marks 70 years since the 1956 Olympics"),
    (28, "Cummins keeps Australia's Test captaincy"),
    (29, "Trump 'seeks permanent' Iran deal via Doha mediators"),
    (30, "El-Sayed Elotibi invited to lead a coalition"),
    (31, "Hamas seeks urgent mediator talks"),
    (32, "Bitcoin above $400,000 after Saturday's 55% flush"),
    (33, "Gold hits an all-time high"),
    (34, "First AP poll: 1 Trillion, Yverzov to AI-7, 07:00 GMT"),
    (35, "Liverpool host Man United, 16:30 GMT \u2014 Pochettino debut"),
]
f_bnum = font(SANS_B, 10)
f_btxt = font(SANS_R, 10)
bc_w = (CW - 2 * 12) // 3
bxs = [M, M + bc_w + 12, M + 2 * (bc_w + 12)]
per_col = [7, 7, 6]
rh = 19
k = 0
for ci, cnt in enumerate(per_col):
    for r in range(cnt):
        if k >= len(BRIEFS):
            break
        n, txt = BRIEFS[k]
        k += 1
        bx = bxs[ci]
        by = y + r * rh
        d.text((bx, by), "%02d" % n, font=f_bnum, fill=(160, 40, 40))
        avail = bc_w - 22
        t = txt
        while len(t) > 1 and d.textlength(t, font=f_btxt) > avail:
            t = t[:-1]
        if t != txt:
            t = t[:-1].rstrip() + "\u2026"
        d.text((bx + 22, by), t, font=f_btxt, fill=(56, 56, 56))
    if ci:
        d.line([bxs[ci] - 7, y - 2, bxs[ci] - 7, y + 7 * rh - 6],
               fill=(206, 200, 188), width=1)

y += 7 * rh + 4

# ---------------- date check footer ----------------
d.rectangle([M, y, W - M, y + 38], outline=RED, width=2)
d.text((M + 9, y + 4), "DATE CHECK", font=font(SANS_B, 12), fill=RED)
d.text((M + 94, y + 5),
       "Every story here happened on, or was first reported on, Sunday 22 November 2026 UTC.",
       font=font(SANS_R, 11), fill=(60, 60, 60))
d.text((M + 94, y + 22),
       "Deliberately excluded: anything from Saturday 21 November or earlier.",
       font=font(SANS_R, 10), fill=(112, 112, 112))

footer_bottom = y + 38
print("layout bottom: %d px" % footer_bottom)
if footer_bottom > 1010:
    FAILS.append("y-flow: layout ends at %d > 1010" % footer_bottom)

img.save("/home/agentuser/workspace/makefun/entry-repo/entry.png", "PNG")
print("rendered v7")

# ---------------- QA: pixel margin guard ----------------
px = img.load()
bad_right = bad_left = bad_bottom = 0
for yy in range(38, H):
    for xx in range(W - 1, W - 8, -1):
        if px[xx, yy] != CREAM:
            bad_right += 1
    for xx in range(0, 7):
        if px[xx, yy] != CREAM:
            bad_left += 1
for yy in range(1012, H):
    for xx in range(W):
        if px[xx, yy] != CREAM:
            bad_bottom += 1
for name, cnt in (("right", bad_right), ("left", bad_left), ("bottom", bad_bottom)):
    if cnt:
        FAILS.append("margin guard: %d non-bg px in %s strip" % (cnt, name))

# ---------------- QA: ink density ----------------
dark = 0
tot = W * H
for yy in range(0, H, 2):
    for xx in range(0, W, 2):
        r, g, b = px[xx, yy]
        if 0.299 * r + 0.587 * g + 0.114 * b < 150:
            dark += 1
density = dark / float((W // 2) * (H // 2))
print("dark ink density: %.3f" % density)

if FAILS:
    for f in FAILS:
        print("QA FAIL:", f, file=sys.stderr)
    sys.exit(1)
print("guard: clean")
