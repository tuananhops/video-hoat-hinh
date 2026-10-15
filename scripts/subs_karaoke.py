#!/usr/bin/env python3
"""Phụ đề hiệu ứng (ASS): faster-whisper large-v3 -> từng chữ, từ đang đọc sáng vàng, bật lên (pop), nằm sát đáy.
Phiên âm THEO ĐOẠN (--chunk giây) để tránh ảo giác kiểu "subscribe"; sửa tên riêng bằng --fix (JSON {"sai":"đúng"}).
Ví dụ: python subs_karaoke.py in.mp4 --fix fix.json --brand LAMIR -o subs.ass --burn out.mp4
       python subs_karaoke.py in.mp4 --words words.json ...   (bỏ qua whisper, dùng [{"w","s","e"}] có sẵn)"""
import argparse, json, os, subprocess, tempfile
from common import run, need, find_font, duration

def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def transcribe(video, model, chunk, lang):
    from faster_whisper import WhisperModel
    wm = WhisperModel(model, device="auto", compute_type="auto")
    D = duration(video); words = []; t0 = 0.0
    while t0 < D:
        wav = tempfile.mktemp(suffix=".wav")
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(t0), "-t", str(chunk), "-i", video, "-ac", "1", "-ar", "16000", wav])
        segs, _ = wm.transcribe(wav, language=lang, word_timestamps=True, vad_filter=True,
                                condition_on_previous_text=False)
        for sg in segs:
            for w in sg.words or []:
                words.append({"w": w.word.strip(), "s": t0 + w.start, "e": t0 + w.end})
        os.remove(wav); t0 += chunk
    bad = {"subscribe", "đăng ký kênh", "hãy subscribe"}
    return [w for w in words if w["w"].lower() not in bad]

def build_ass(words, W, H, font, fs, per_line, hi, brand, brand_color, margin):
    fam = "Be Vietnam Pro" if "BeVietnam" in font else "DejaVu Sans"
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: K,{fam},{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,2,2,40,40,{margin},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    def bgr(hexc): hexc = hexc.lstrip("#"); return f"&H00{hexc[4:6]}{hexc[2:4]}{hexc[0:2]}&"
    lines = []
    for i in range(0, len(words), per_line):
        grp = words[i:i + per_line]
        for j, cur in enumerate(grp):
            end = grp[j + 1]["s"] if j + 1 < len(grp) else cur["e"] + 0.15
            parts = []
            for k, w in enumerate(grp):
                base = bgr(brand_color) if brand and brand.lower() in w["w"].lower() else "&H00FFFFFF&"
                if k == j:
                    parts.append(r"{\c" + bgr(hi) + r"\fscx115\fscy115\t(0,120,\fscx100\fscy100)}" + w["w"] + r"{\r}")
                else:
                    parts.append(r"{\c" + base + "}" + w["w"] + r"{\r}")
            pop = r"{\fad(60,0)}" if j == 0 else ""
            lines.append(f"Dialogue: 0,{ts(cur['s'])},{ts(end)},K,,0,0,0,,{pop}{' '.join(parts)}")
    return head + "\n".join(lines) + "\n"

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("video"); p.add_argument("--words"); p.add_argument("--model", default="large-v3")
    p.add_argument("--chunk", type=float, default=20); p.add_argument("--lang", default="vi")
    p.add_argument("--fix", help="JSON map sửa chữ"); p.add_argument("--per-line", type=int, default=4)
    p.add_argument("--highlight", default="#FFD400"); p.add_argument("--brand"); p.add_argument("--brand-color", default="#1E6FFF")
    p.add_argument("--size", default="1080x1920"); p.add_argument("--fontsize", type=int)
    p.add_argument("--margin", type=int, help="khoảng cách đáy (px); mặc định 6% chiều cao")
    p.add_argument("-o", "--out", default="subs.ass"); p.add_argument("--burn", help="xuất video đã đốt phụ đề")
    a = p.parse_args(); need("ffmpeg")
    words = json.load(open(a.words, encoding="utf-8")) if a.words else transcribe(a.video, a.model, a.chunk, a.lang)
    fix = json.load(open(a.fix, encoding="utf-8")) if a.fix else {}
    for w in words:
        for k, v in fix.items():
            if w["w"].lower().strip(".,!?") == k.lower(): w["w"] = v
    W, H = map(int, a.size.split("x")); font = find_font()
    ass = build_ass(words, W, H, font, a.fontsize or int(W * 0.065), a.per_line, a.highlight, a.brand,
                    a.brand_color, a.margin or int(H * 0.06))
    open(a.out, "w", encoding="utf-8").write(ass); print("OK", a.out, len(words), "từ")
    if a.burn:
        fd = os.path.dirname(font)
        run(["ffmpeg", "-y", "-v", "error", "-i", a.video, "-vf", f"ass={a.out}:fontsdir={fd}", "-c:a", "copy", a.burn])
        print("OK", a.burn)

if __name__ == "__main__":
    main()
