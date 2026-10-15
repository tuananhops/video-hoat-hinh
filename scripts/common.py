"""Tiện ích chung: chạy ffmpeg, đo thời lượng, tìm font."""
import json, shutil, subprocess, glob, os

def run(cmd):
    print("+", " ".join(map(str, cmd))[:300])
    subprocess.run(list(map(str, cmd)), check=True)

def duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", str(path)])
    return float(out.strip())

def find_font(name="BeVietnamPro-Bold"):
    for d in ["/usr/share/fonts", os.path.expanduser("~/.local/share/fonts"), "/usr/local/share/fonts"]:
        hits = glob.glob(f"{d}/**/{name}*.ttf", recursive=True)
        if hits:
            return hits[0]
    hits = glob.glob("/usr/share/fonts/**/DejaVuSans-Bold.ttf", recursive=True)
    return hits[0] if hits else ""

def load_config(path):
    with open(path, encoding="utf-8") as f:
        if path.endswith((".yaml", ".yml")):
            import yaml
            return yaml.safe_load(f)
        return json.load(f)

def need(binary):
    if not shutil.which(binary):
        raise SystemExit(f"Thiếu {binary}. Xem scripts/README.md")
