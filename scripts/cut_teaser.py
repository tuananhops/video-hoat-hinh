#!/usr/bin/env python3
"""Cắt bản mẫu/teaser N giây (mặc định 14s từ đầu), fade hình + tiếng ở cuối.
Ví dụ: python cut_teaser.py final.mp4 --length 10 -o teaser_10s.mp4"""
import argparse
from common import run, need

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("video"); p.add_argument("--start", type=float, default=0)
    p.add_argument("--length", type=float, default=14); p.add_argument("--fade", type=float, default=1.0)
    p.add_argument("-o", "--out", default="teaser.mp4")
    a = p.parse_args(); need("ffmpeg"); st = a.length - a.fade
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(a.start), "-i", a.video, "-t", str(a.length),
         "-vf", f"fade=t=out:st={st}:d={a.fade}", "-af", f"afade=t=out:st={st}:d={a.fade}",
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", a.out])
    print("OK", a.out)

if __name__ == "__main__":
    main()
