#!/usr/bin/env python3
"""Thêm nhạc nền + SFX: sidechain ducking dưới giọng, fade, loudnorm -14 LUFS / TP -1.5.
Nhạc phải NGHE RÕ: mặc định nhạc ~ -8..-9 dB dưới giọng khi đang đọc (bản đầu từng bị nhỏ không nghe thấy).
Ví dụ: python add_music.py in.mp4 --music track.mp3 --music-gain 0 --sfx "whoosh.wav@3.2" "zap.wav@14:+2" -o out.mp4"""
import argparse
from common import run, duration, need

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("video"); p.add_argument("--music", required=True)
    p.add_argument("--music-gain", type=float, default=0, help="dB cho nhạc trước khi duck")
    p.add_argument("--duck-ratio", type=float, default=4); p.add_argument("--duck-threshold", type=float, default=0.05)
    p.add_argument("--music-start", type=float, default=0); p.add_argument("--fade-in", type=float, default=1)
    p.add_argument("--fade-out", type=float, default=3)
    p.add_argument("--sfx", nargs="*", default=[], help="file@giây[:gaindB]")
    p.add_argument("--lufs", type=float, default=-14); p.add_argument("--tp", type=float, default=-1.5)
    p.add_argument("-o", "--out", default="with_music.mp4")
    a = p.parse_args(); need("ffmpeg"); D = duration(a.video)
    inputs = ["-i", a.video, "-ss", str(a.music_start), "-stream_loop", "-1", "-i", a.music]
    fc = [f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[vo][sc]",
          f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={a.music_gain}dB,atrim=0:{D},"
          f"afade=t=in:d={a.fade_in},afade=t=out:st={max(0, D-a.fade_out)}:d={a.fade_out}[m]",
          f"[m][sc]sidechaincompress=threshold={a.duck_threshold}:ratio={a.duck_ratio}:attack=20:release=400[md]"]
    mix = ["[vo]", "[md]"]
    for k, s in enumerate(a.sfx):
        f, rest = s.rsplit("@", 1); t, g = (rest.split(":") + ["0"])[:2]
        inputs += ["-i", f]; ms = int(float(t) * 1000)
        fc.append(f"[{k+2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[x{k}]")
        mix.append(f"[x{k}]")
    fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,"
              f"loudnorm=I={a.lufs}:TP={a.tp}:LRA=11[a]")
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{D:.3f}", a.out])
    print("OK", a.out)

if __name__ == "__main__":
    main()
