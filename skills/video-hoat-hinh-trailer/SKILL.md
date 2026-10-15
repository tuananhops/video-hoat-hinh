---
name: video-hoat-hinh-trailer
description: Quy trình làm video hoạt hình/explainer marketing có thuyết minh tiếng Việt (trailer tín dụng BĐS 16:9, quảng cáo đại lý 9:16) từ kịch bản docx hoặc bảng cảnh. Đọc trước khi nhận bất kỳ việc làm video nào.
---
# Video hoạt hình: pipeline đầy đủ

## 0. Chuẩn bị
- Cài theo `scripts/README.md`. Kiểm tra font Be Vietnam Pro (`fc-list | grep -i vietnam`).
- Tạo thư mục dự án; mọi file tạm (caption txt…) để trong thư mục dự án, không để `/tmp`.

## 1. Đọc kịch bản
- Liệt kê cảnh, lời thoại, **mọi con số** (ngày, số tỷ đồng, tên ngân hàng/chi nhánh).
- Tỉ lệ: mặc định 9:16; "video ngang" → 16:9 (1920x1080).

## 2. Phân tích tham khảo
- Video tham khảo: dùng mô hình phân tích video (nhịp, màu, chữ, nhạc). Ví dụ: trailer vàng–xanh, chữ serif vàng; quảng cáo đại lý: MC nói trước camera, chữ pop-up, hotline.

## 3. Prompt và sinh clip
- Viết *character sheet* một lần rồi dán vào mọi prompt: tên, tuổi, **màu tóc** (giữ cố định; từng ra tóc trắng sai), trang phục, màu chủ đạo (ví dụ đối tác mặc đỏ).
- Mô hình tòa nhà = ảnh thật. Đổi ảnh sang png, để trong thư mục riêng của bot, truyền làm ảnh tham chiếu.
- Không để AI vẽ biển hiệu ngân hàng (từng ra chữ "HIỆP PHÁT"); chỉ hiển thị tên viết tắt đúng bằng logo/caption dán sau.
- Mỗi cảnh: 1 clip chính + 1–2 clip phụ để lấp thời lượng ở **tốc độ thường**.
- Executor không gọi được công cụ sinh video: agent chính phải tự sinh.
- ⛔ DỪNG: gửi chủ xem khung hình các clip chính.

## 4. VO
`python scripts/tts_vi.py --lines vo.txt --outdir vo/` (gTTS → trim lặng → 1.39x → +3 dB).
Giọng nhân bản: OmniVoice (k2-fsa) trong venv riêng, chạy CPU được, đầu vào là mp3 mẫu của chủ.

## 5. Ráp
`python scripts/assemble.py config.json -o assembled.mp4` (xem `examples/`).
- Tiếng clip AI bị bỏ hoàn toàn.
- Caption: fontsize 48–50 (tránh tràn), sát đáy, có dải tối.
- Thẻ giới thiệu nhân vật: `intro_card` (đứng hình ~2s + tên/chức danh). Không dùng pill tag.
- Logo ngân hàng/thương hiệu: `logos` ở góc trên trái.

## 6. Nhạc, SFX, phụ đề
- `python scripts/gen_sfx.py --outdir sfx`
- `python scripts/add_music.py assembled.mp4 --music track.mp3 --sfx sfx/whoosh.wav@3.2 sfx/hit.wav@0:+2 -o final.mp4`
  - Nhạc phải nghe rõ (~8–9 dB dưới giọng). Đoạn buồn thì đổi nhạc/hạ nhịp.
  - Nhạc CC BY (Kevin MacLeod, incompetech): ghi nguồn "Tên bài – Kevin MacLeod (incompetech.com), CC BY 4.0".
- Phụ đề karaoke: `python scripts/subs_karaoke.py final.mp4 --fix fix.json --brand LAMIR --burn final_sub.mp4`

## 7–8. Duyệt và giao
- ⛔ DỪNG gửi chủ xem → áp ghi chú khách → gửi lại.
- ⛔ Chỉ upload Drive khi chủ bảo (connector Drive, UploadFile). Teaser: `scripts/cut_teaser.py --length 14`.
