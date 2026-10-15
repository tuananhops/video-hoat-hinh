#!/usr/bin/env python3
"""Tạo SFX tổng hợp bằng ffmpeg: whoosh, zap (tia điện), ding, hit (trống trailer).
Ví dụ: python gen_sfx.py --outdir sfx/   -> sfx/whoosh.wav, zap.wav, ding.wav, hit.wav"""
import argparse, os
from common import run, need

RECIPES = {
    "whoosh": ("anoisesrc=d=0.8:c=pink:a=0.6", "bandpass=f=1200:w=1500,afade=t=in:d=0.35,afade=t=out:st=0.4:d=0.4"),
    "zap": ("anoisesrc=d=0.35:c=white:a=0.7", "highpass=f=2500,tremolo=f=40:d=0.9,afade=t=out:st=0.15:d=0.2"),
    "ding": ("sine=f=1318:d=1.2", "afade=t=out:st=0.05:d=1.15,volume=0.6"),
    "hit": ("sine=f=55:d=1.0", "afade=t=out:st=0.05:d=0.9,volume=1.5"),
}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outdir", default="sfx"); p.add_argument("--only", nargs="*")
    a = p.parse_args(); need("ffmpeg"); os.makedirs(a.outdir, exist_ok=True)
    for name, (src, af) in RECIPES.items():
        if a.only and name not in a.only: continue
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", src, "-af", af, "-ar", "48000", "-ac", "2",
             os.path.join(a.outdir, f"{name}.wav")])

if __name__ == "__main__":
    main()
