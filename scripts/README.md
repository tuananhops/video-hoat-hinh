# scripts/

## Cài đặt
```bash
sudo apt-get install -y ffmpeg fonts-dejavu   # ffmpeg cần libass + libx264
# Font Be Vietnam Pro: tải từ Google Fonts, chép *.ttf vào ~/.local/share/fonts && fc-cache -f
python3 -m venv .venv && . .venv/bin/activate
pip install -r scripts/requirements.txt
```

## Công cụ
| Script | Việc |
|---|---|
| `tts_vi.py` | gTTS tiếng Việt + trim lặng + 1.39x + 3 dB (`--offline` để test không mạng) |
| `assemble.py` | Ráp theo config JSON/YAML: clip, fill, VO, caption, logo, intro_card |
| `add_music.py` | Nhạc + ducking + fade + SFX cue + loudnorm -14/-1.5 |
| `subs_karaoke.py` | faster-whisper → ASS tô chữ + pop, sát đáy, map sửa chữ, `--burn` |
| `cut_teaser.py` | Cắt teaser N giây có fade |
| `gen_sfx.py` | Tổng hợp whoosh, zap, ding, hit |

## Test nhanh
```bash
ffmpeg -f lavfi -i testsrc=s=640x360:d=2 -f lavfi -i sine=d=2 -shortest a.mp4
python scripts/tts_vi.py --text "Xin chào" -o vo1.wav
python scripts/gen_sfx.py --outdir sfx
```
