# 01 - CHUẨN BỊ GITHUB

## A. Kiểm tra dự án trước khi upload

Tại thư mục dự án chạy:

```bash
python tools/check_project.py
```

Nếu kết thúc bằng `SAN SANG DEPLOY` thì tiếp tục.

## B. Tạo repository

1. Đăng nhập GitHub.
2. Chọn `New repository`.
3. Đặt tên gợi ý: `canh-giac-online`.
4. Chọn Public nếu muốn triển khai đơn giản bằng Streamlit Community Cloud.
5. Tạo repository.

## C. Upload

Upload TOÀN BỘ NỘI DUNG thư mục dự án, không upload file ZIP.

Cấu trúc gốc cần có:

```text
app.py
requirements.txt
README.md
START_HERE.md
data/
model/
modules/
.streamlit/config.toml
```

KHÔNG upload Secrets hoặc file khóa JSON.

## D. Kiểm tra trên GitHub

Phải nhìn thấy:

```text
model/classifier.joblib
data/messages.csv
data/situations.csv
data/pretest.csv
data/posttest.csv
```
