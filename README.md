# CẢNH GIÁC ONLINE - BỘ TRIỂN KHAI HOÀN CHỈNH

Phiên bản dành cho giáo viên/học sinh THCS, gồm:

- Mô hình TF-IDF + Logistic Regression đã huấn luyện trên bộ 800 mẫu mô phỏng cân bằng.
- Giao diện Streamlit tối ưu điện thoại.
- 30 tình huống luyện tập.
- Theo dõi tiến bộ bằng mã học sinh ẩn danh.
- Google Sheets làm kho dữ liệu tập trung.
- Pre-test 20 câu + Post-test 20 câu.
- Dashboard giáo viên + xuất CSV.
- Bộ 60 mã nghiên cứu mẫu: 30 thực nghiệm + 30 đối chứng.
- Công cụ kiểm tra dự án và tạo Streamlit Secrets.
- Dockerfile cho phương án Google Cloud Run tùy chọn.

## Bắt đầu

Mở `START_HERE.md` và làm đúng thứ tự.

## Chạy cục bộ

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Kiểm tra trước deploy

```bash
python tools/check_project.py
```

## Kho dữ liệu

- Nếu có Streamlit Secrets hợp lệ: Google Sheets.
- Nếu chưa cấu hình: SQLite cục bộ (chỉ dùng phát triển/kiểm thử).

## Bảo mật

Không commit `.streamlit/secrets.toml`, Service Account JSON, `credentials.json` hoặc `data/progress.db` lên GitHub.
