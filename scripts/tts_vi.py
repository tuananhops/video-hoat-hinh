#!/usr/bin/env python3
"""Thuyết minh tiếng Việt bằng gTTS + cắt khoảng lặng + tăng tốc + tăng âm.
Ví dụ: python tts_vi.py --text "Xin chào" -o vo1.wav
       python tts_vi.py --lines vo.txt --outdir vo/   (mỗi dòng 1 file vo1.wav, vo2.wav...)"""
import argparse, os, tempfile
from common import run, need

def synth(text, out, speed, gain, lang, offline):
    tmp = tempfile.mktemp(suffix=".mp3")
    if offline:  # dùng khi không có mạng: tạo tiếng giả để test pipeline
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=f=220:d=%.2f" % max(1, len(text) / 15), tmp])
    else:
        from gtts import gTTS
        gTTS(text, lang=lang).save(tmp)
    af = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          f"atempo={speed},volume={gain}dB")
    run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", af, "-ar", "48000", out])
    os.remove(tmp)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--text"); p.add_argument("--lines", help="file txt, mỗi dòng 1 câu")
    p.add_argument("-o", "--out", default="vo.wav"); p.add_argument("--outdir", default=".")
    p.add_argument("--speed", type=float, default=1.39); p.add_argument("--gain", type=float, default=3)
    p.add_argument("--lang", default="vi"); p.add_argument("--offline", action="store_true")
    a = p.parse_args(); need("ffmpeg")
    if a.lines:
        os.makedirs(a.outdir, exist_ok=True)
        lines = [l.strip() for l in open(a.lines, encoding="utf-8") if l.strip()]
        for i, t in enumerate(lines, 1):
            synth(t, os.path.join(a.outdir, f"vo{i}.wav"), a.speed, a.gain, a.lang, a.offline)
    elif a.text:
        synth(a.text, a.out, a.speed, a.gain, a.lang, a.offline)
    else:
        p.error("cần --text hoặc --lines")

if __name__ == "__main__":
    main()
