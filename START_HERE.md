# BẮT ĐẦU TỪ ĐÂY - CẢNH GIÁC ONLINE

Bộ này đã sẵn sàng để triển khai cho học sinh dùng trên điện thoại.

## Kiến trúc khuyến nghị

Điện thoại học sinh → Streamlit Community Cloud → Google Sheets của giáo viên.

- GitHub: lưu mã nguồn.
- Streamlit Community Cloud: chạy app và tạo đường link công khai.
- Google Sheets: lưu kết quả học sinh bền vững.
- Service Account: cho phép app ghi dữ liệu vào Google Sheets mà học sinh không cần đăng nhập Gmail.

## Thứ tự triển khai

1. Đọc `01_CHUAN_BI_GITHUB.md`.
2. Đọc `02_CAU_HINH_GOOGLE_SHEETS.md`.
3. Chạy `python tools/make_secrets.py ...` để tạo Secrets nhanh (không bắt buộc).
4. Đọc `03_DEPLOY_STREAMLIT.md` để đưa app lên Internet.
5. Đọc `05_CHECKLIST_TRUOC_KHI_PHAT_LINK.md` và kiểm thử.
6. Gửi đường link/QR cho học sinh.
7. Học sinh đọc `04_HUONG_DAN_HOC_SINH.md`.

## Tệp quan trọng

- `app.py`: ứng dụng chính.
- `model/classifier.joblib`: mô hình ML đã huấn luyện.
- `data/messages.csv`: 800 mẫu dữ liệu huấn luyện/nghiên cứu.
- `data/situations.csv`: câu hỏi luyện tập.
- `data/pretest.csv`, `data/posttest.csv`: bài Pre/Post.
- `data/students.csv`: mã HS nghiên cứu.
- `.streamlit/secrets.toml.example`: mẫu Secrets.
- `modules/storage.py`: lưu Google Sheets hoặc SQLite dự phòng.

## Lưu ý bảo mật

KHÔNG đưa lên GitHub:
- `.streamlit/secrets.toml`
- file JSON Service Account
- `credentials.json`
- `data/progress.db`

`.gitignore` đã được cấu hình để chặn các tệp này.
