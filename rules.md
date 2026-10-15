# rules.md: Quy tắc công việc

## Quy tắc nội dung
1. VO luôn tiếng Việt. Không bao giờ để lọt tiếng Anh (bỏ hết tiếng gốc clip AI).
2. Tỉ lệ mặc định 9:16; 16:9 khi khách yêu cầu ("video ngang").
3. Caption/phụ đề nằm sát đáy, **không bao giờ che mặt**.
4. Nhân vật nhất quán: màu tóc, trang phục cố định (một clip từng ra nhân vật chính tóc trắng → phải làm lại tóc đen).
5. Không làm chậm/đứng hình để kéo thời lượng (trông không chuyên nghiệp); lấp bằng clip bổ sung chạy tốc độ thường.
6. Mô hình tòa nhà phải giống ảnh thật, giữ nguyên từ đầu đến cuối; chỉ thay đổi công năng.
7. Không để biển hiệu ngân hàng giả (AI từng vẽ chữ "HIỆP PHÁT"); chỉ hiển thị đúng tên viết tắt ngân hàng (ví dụ "PGB", "Vietinbank Bắc Đà Nẵng").
8. Kết thúc tiết chế khi khách yêu cầu: không pháo hoa, không đám đông (ví dụ chỉ 3 bên bắt tay rồi tối dần).
9. Giữ đúng mọi con số trong kịch bản.
10. Nhạc CC BY phải ghi nguồn. Bài học: không có bản "3 Strikes" hợp pháp miễn phí → báo chủ, dùng bài thay thế (Motivator) và xin file nếu chủ có.
11. Thẻ giới thiệu nhân vật kiểu phim; không dùng pill name tag nhỏ.
12. Hotline/số điện thoại lấy từ kịch bản của khách; trong repo dùng placeholder 09xx.xxx.xxx.

## Cài đặt bắt buộc
- ffmpeg/ffprobe (có libass, libx264), Python 3.10+, `pip install -r scripts/requirements.txt`.
- Font Be Vietnam Pro (Bold/ExtraBold).
- Tùy chọn: OmniVoice (venv riêng) để nhân bản giọng; yt-dlp.

## Lỗi đã mắc và bài học
- Executor/subagent không gọi được công cụ sinh video → agent chính tự sinh clip.
- Ảnh tham chiếu jpeg ở thư mục workspace báo "Could not read" → chuyển png, để trong thư mục riêng của bot.
- `drawtext textfile` đặt trong `/tmp` bị mất → để trong thư mục dự án.
- Caption tràn ngang → fontsize 48–50.
- edge-tts trả 403 → dùng gTTS.
- Tiếng gốc clip AI đè lời thuyết minh, có tiếng Anh → bỏ hết, chỉ VO + nhạc.
- Nhạc bản đầu quá nhỏ, chủ không nghe thấy → nhạc ~8–9 dB dưới giọng, đo bằng loudnorm/ebur128 và nghe lại.
- Whisper ảo giác dòng "subscribe" → phiên âm theo đoạn, tắt condition_on_previous_text, lọc từ rác, sửa tên thương hiệu bằng tay.
- File Drive > 100MB: tải bằng connector Drive (DownloadFile) hoặc yt-dlp; yt-dlp có lúc lỗi 400 → dùng Drive API/connector.
- Làm chậm cảnh để khớp VO → chủ chê → thêm clip phụ.

## Ghi chú công cụ
- Sinh video AI: 16:9 hoặc 9:16, 720p, nhận `reference_image_paths`; nhiều lệnh song song được.
- Drive: UploadFile/DownloadFile qua connector; thư mục đích chỉ định bằng folderId.
- Kiểm tra kết quả: trích lưới khung hình (`ffmpeg -vf fps=1/5,tile`) để soi tóc, chữ, caption.
