#!/usr/bin/env python3
"""Ráp video theo file cấu hình (JSON/YAML). Mỗi cảnh: clip + VO + caption + logo + thẻ giới thiệu.
- BỎ HẲN tiếng gốc của clip AI (tránh tiếng Anh, đè lời).
- Clip ngắn hơn VO thì nối thêm clip trong "fill" (KHÔNG làm chậm/đứng hình).
- Caption nằm thấp sát đáy, có dải gradient, không che mặt.
- intro_card: đứng hình 1 frame + thẻ tên kiểu phim (KHÔNG dùng pill tag nhỏ).
Ví dụ: python assemble.py config.json -o out.mp4"""
import argparse, os, tempfile
from common import run, duration, find_font, load_config, need

def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019").replace("%", "\\%")

def build_scene(i, sc, cfg, work):
    W, H = cfg.get("size", [1920, 1080]); fps = cfg.get("fps", 30)
    font = cfg.get("font") or find_font(); color = cfg.get("caption_color", "#E8C66A")
    fs = sc.get("fontsize", cfg.get("caption_fontsize", 50 if W > H else 48))
    vo = sc.get("vo"); pad = sc.get("pad", 0.4)
    dur = sc.get("duration") or (duration(vo) + pad if vo else duration(sc["clip"]))
    clips = [sc["clip"]] + sc.get("fill", [])
    # nối clip chính + clip bổ sung đến khi đủ thời lượng, ở tốc độ thường
    lst = os.path.join(work, f"l{i}.txt")
    with open(lst, "w") as f:
        tot, k = 0, 0
        while tot < dur:
            c = clips[k % len(clips)]; f.write(f"file '{os.path.abspath(c)}'\n"); tot += duration(c); k += 1
    vf = [f"scale={W}:{H}:force_original_aspect_ratio=increase", f"crop={W}:{H}", f"fps={fps}", "setsar=1"]
    inputs = ["-f", "concat", "-safe", "0", "-i", lst]
    fc = [f"[0:v]{','.join(vf)}[v0]"]; last = "v0"; n = 1
    if sc.get("caption"):
        txt = os.path.join(work, f"cap{i}.txt")  # textfile trong thư mục dự án, không để /tmp
        open(txt, "w", encoding="utf-8").write(sc["caption"])
        bar = int(H * 0.16)
        fc.append(f"[{last}]drawbox=x=0:y={H-bar}:w={W}:h={bar}:color=black@0.45:t=fill,"
                  f"drawtext=fontfile='{font}':textfile='{txt}':fontsize={fs}:fontcolor={color}:"
                  f"borderw=3:bordercolor=black@0.8:x=(w-tw)/2:y=h-th-{int(H*0.05)}[c{i}]"); last = f"c{i}"
    for lg in sc.get("logos", []):
        inputs += ["-loop", "1", "-i", lg["path"]]
        lw = lg.get("width", int(W * 0.12))
        fc.append(f"[{n}:v]scale={lw}:-1,format=rgba[lg{n}];[{last}][lg{n}]overlay={lg.get('x',40)}:{lg.get('y',40)}:shortest=1[o{n}]")
        last = f"o{n}"; n += 1
    if vo:
        inputs += ["-i", vo]; amap = ["-map", f"{n}:a"]
    else:
        inputs += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]; amap = ["-map", f"{n}:a"]
    out = os.path.join(work, f"s{i:02d}.mp4")
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc), "-map", f"[{last}]", *amap,
         "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac",
         "-ar", "48000", "-ac", "2", "-af", "apad", out])
    segs = [out]
    if sc.get("intro_card"):
        segs.insert(1, intro_card(i, out, sc["intro_card"], cfg, work, font))
    return segs

def intro_card(i, scene_mp4, card, cfg, work, font):
    """Đứng hình frame tại card.at giây + tên/chức danh kiểu phim (chữ vàng serif/đậm, gạch ngang)."""
    W, H = cfg.get("size", [1920, 1080]); d = card.get("duration", 2.0)
    fr = os.path.join(work, f"fr{i}.png")
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(card.get("at", 1.0)), "-i", scene_mp4, "-frames:v", "1", fr])
    nt = os.path.join(work, f"nm{i}.txt"); rt = os.path.join(work, f"rl{i}.txt")
    open(nt, "w", encoding="utf-8").write(card["name"]); open(rt, "w", encoding="utf-8").write(card.get("role", ""))
    col = card.get("color", cfg.get("caption_color", "#E8C66A"))
    vf = (f"scale={W}:{H},eq=brightness=-0.12:saturation=0.6,drawbox=x={int(W*0.06)}:y={int(H*0.55)}:w={int(W*0.3)}:h=4:color={col}:t=fill,"
          f"drawtext=fontfile='{font}':textfile='{nt}':fontsize={int(H*0.08)}:fontcolor={col}:x={int(W*0.06)}:y={int(H*0.45)}:alpha='min(1,t*3)',"
          f"drawtext=fontfile='{font}':textfile='{rt}':fontsize={int(H*0.04)}:fontcolor=white:x={int(W*0.06)}:y={int(H*0.58)}:alpha='min(1,t*2)'")
    out = os.path.join(work, f"card{i}.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", fr, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-vf", vf, "-t", str(d), "-r", str(cfg.get("fps", 30)), "-c:v", "libx264", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", out])
    return out

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("config"); p.add_argument("-o", "--out", default="assembled.mp4"); p.add_argument("--workdir")
    a = p.parse_args(); need("ffmpeg"); cfg = load_config(a.config)
    base = os.path.dirname(os.path.abspath(a.config))
    for sc in cfg["scenes"]:  # đường dẫn tương đối tính theo file config
        for k in ("clip", "vo"):
            if sc.get(k) and not os.path.isabs(sc[k]): sc[k] = os.path.join(base, sc[k])
        sc["fill"] = [f if os.path.isabs(f) else os.path.join(base, f) for f in sc.get("fill", [])]
        for lg in sc.get("logos", []):
            if not os.path.isabs(lg["path"]): lg["path"] = os.path.join(base, lg["path"])
    work = a.workdir or os.path.join(base, "_work"); os.makedirs(work, exist_ok=True)
    segs = []
    for i, sc in enumerate(cfg["scenes"], 1): segs += build_scene(i, sc, cfg, work)
    lst = os.path.join(work, "all.txt")
    open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", a.out])
    print(f"OK {a.out} {duration(a.out):.2f}s")

if __name__ == "__main__":
    main()
