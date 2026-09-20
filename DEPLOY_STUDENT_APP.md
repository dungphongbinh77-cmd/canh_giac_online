# DEPLOY BẢN HỌC SINH

## 1. Chuẩn bị mã học sinh

Mở `data/student_codes.csv`.

Mặc định có 100 mã `HS001` đến `HS100`. Có thể sửa cột `class_name` và đặt `active=0` cho mã chưa dùng.

## 2. Upload lên GitHub

Tạo repository mới, ví dụ `canh-giac-online-student`.

Upload toàn bộ nội dung trong thư mục `01_STUDENT_APP`, không upload file ZIP.

## 3. Streamlit Secrets

Dùng cùng `spreadsheet_id` và Service Account đã thử nghiệm thành công.

Dán nội dung Secrets vào:

`Streamlit Community Cloud > App > Settings > Secrets`

Không cần `admin_pin` cho bản học sinh.

## 4. Deploy

- Repository: repository bản học sinh.
- Branch: `main`.
- Main file: `app.py`.

## 5. Kiểm tra trước khi phát link

Dùng mã `HS001`:

1. Mở app trên điện thoại.
2. Vào Kiểm tra thông điệp và phân tích một tin nhắn mẫu.
3. Làm ít nhất 2 câu Thử thách.
4. Vào Tiến bộ của tôi và kiểm tra số lượt đã ghi nhận.
5. Mở Google Sheet kiểm tra `quiz_attempts` và `message_checks` có thêm dữ liệu.

Chỉ phát link sau khi cả 5 bước đều đạt.
