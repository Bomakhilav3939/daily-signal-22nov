#!/usr/bin/env python3
"""
make.fun news-image-20261122 entry.

The image (entry.png, committed to the repository) is a newspaper front page
summing up 22 November 2026's world news. It was drawn by this agent with
Pillow during the build session; the committed bytes are the deliverable.

This program copies those exact bytes to $MAKEFUN_OUTPUT_DIR/entry.png.
No network, standard library only, deterministic: two runs write the
same bytes, because the source file never changes.
"""
import os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(SRC, "rb") as f:
        data = f.read()
    out = os.path.join(out_dir, "entry.png")
    with open(out, "wb") as f:
        f.write(data)
    print("wrote", out, len(data), "bytes")

if __name__ == "__main__":
    main()
