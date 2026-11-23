#!/usr/bin/env python3
"""
make.fun news-image-20261122 — deterministic newspaper front page generator.
Reads news22.json (committed to repo), renders a 1024x1024 PNG front page.
No network, stdlib + PIL only. Two runs produce byte-identical output
(PIL PNG encoder is deterministic for identical input/params).
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
INK = (22, 11, 47)
PAPER = (250, 246, 240)
ACCENT = (214, 32, 60)      # masthead red
MUTED = (110, 104, 122)
RULE = (60, 50, 80)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"

def F(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

def load_news():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "news22.json")) as f:
        return json.load(f)

def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def _clean(text, n):
    text = text.strip()
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(" ", 1)[0]
    return cut.rstrip(",;:. ") + "…"


def main():
    news = load_news()
    day = news["day"]  # 2026-11-22
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    f_mast = F("DejaVuSerif-Bold.ttf", 60)
    f_date = F("DejaVuSans-Bold.ttf", 46)
    f_kick = F("DejaVuSans-Bold.ttf", 21)
    f_head = F("DejaVuSerif-Bold.ttf", 40)
    f_head2 = F("DejaVuSerif.ttf", 28)
    f_body = F("DejaVuSans.ttf", 19)
    f_region = F("DejaVuSans-Bold.ttf", 18)

    # ---- masthead ----
    d.text((40, 34), "THE DAILY SIGNAL", font=f_mast, fill=INK)
    d.text((40, 102), "SUNDAY, NOVEMBER 22, 2026", font=f_date, fill=ACCENT)
    d.text((40, 142), "36 STORIES  •  7 REGIONS  •  THE WORLD IN ONE PAGE",
           font=f_kick, fill=MUTED)
    d.line((40, 178, W - 40, 178), fill=INK, width=4)
    d.line((40, 184, W - 40, 184), fill=INK, width=1)

    # ---- columns: 2 columns below masthead ----
    col_x = [40, 540]
    col_w = 444
    y = [206, 206]

    def story_head(ci, tier, headline, place):
        x = col_x[ci]
        yy = y[ci]
        if tier == "lead":
            font = f_head
            d.rectangle((x - 6, yy, x + col_w + 6, yy + 2), fill=ACCENT)
            yy += 10
        else:
            font = f_head2
        lines = wrap(d, headline.upper() if tier == "lead" else headline,
                     font, col_w)
        for ln in lines:
            d.text((x, yy), ln, font=font,
                   fill=INK if tier == "lead" else (40, 34, 66))
            yy += font.size + 4
        if place:
            plines = wrap(d, "— " + place, f_body, col_w)
            for pln in plines:
                d.text((x, yy), pln, font=f_body, fill=MUTED)
                yy += f_body.size + 4
        yy += 8
        y[ci] = yy

    def story_sub(ci, text):
        x = col_x[ci]
        lines = wrap(d, text, f_body, col_w)
        for ln in lines[:3]:
            d.text((x, y[ci]), ln, font=f_body, fill=MUTED)
            y[ci] += f_body.size + 3
        y[ci] += 10

    # leads get both columns? keep simple: lead1 col0, then col1; cards/briefs flow
    items = [s for s in news["stories"] if s.get("tier") in ("lead", "card")]
    briefs = [s for s in news["stories"] if s.get("tier") == "brief"]

    def hl(s):
        return s.get("headline") or s.get("tldr", {}).get("hook", "")

    # lead stories
    story_head(0, "lead", hl(news["stories"][0]), news["stories"][0].get("place"))
    story_sub(0, _clean(news["stories"][0].get("summary", ""), 220))
    story_head(1, "lead", hl(news["stories"][2]), news["stories"][2].get("place"))
    story_sub(1, _clean(news["stories"][2].get("summary", ""), 220))

    # second lead + climate (story 2) goes col0 below
    story_head(0, "card", hl(news["stories"][1]), news["stories"][1].get("place"))
    story_sub(0, _clean(news["stories"][1].get("summary", ""), 200))

    # fill remaining cards alternating columns
    for s in items:
        if s["n"] in (1, 3, 2):
            continue
        ci = 0 if y[0] <= y[1] else 1  # kolom paling kosong dulu (balance)
        if y[ci] > H - 430:
            if y[1 - ci] <= H - 430:
                ci = 1 - ci
            else:
                break
        story_head(ci, s.get("tier", "card"), hl(s), s.get("place"))

    # ---- briefs ticker at bottom (single column, full width, no overlap) ----
    yb = H - 262
    d.line((40, yb - 16, W - 40, yb - 16), fill=INK, width=3)
    d.text((40, yb - 10), "ALSO TODAY", font=f_region, fill=ACCENT)
    yb += 20
    for i, s in enumerate(briefs[:9]):
        if yb > H - 52:
            break
        d.text((40, yb), "• " + hl(s)[:78], font=f_body, fill=INK)
        yb += 26

    # ---- footer rule ----
    d.line((40, H - 34, W - 40, H - 34), fill=INK, width=2)
    d.text((40, H - 28), "PAGE ONE — EVERY STORY DATED 22 NOVEMBER 2026",
           font=f_kick, fill=INK)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "entry.png")
    im.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")

if __name__ == "__main__":
    main()
