# 03 - DEPLOY STREAMLIT COMMUNITY CLOUD

## A. Kết nối GitHub

1. Vào `https://share.streamlit.io`.
2. Đăng nhập bằng GitHub.
3. Cho phép Streamlit truy cập repository chứa app.

## B. Tạo app

1. Chọn `Create app`.
2. Chọn repository `canh-giac-online`.
3. Branch: `main`.
4. Main file path: `app.py`.
5. Đặt App URL, ví dụ `canh-giac-online-phong-dinh` nếu còn trống.

## C. Thêm Secrets

Trước khi Deploy hoặc trong App settings > Secrets:

1. Mở file `.streamlit/secrets.toml` trên máy.
2. Copy toàn bộ nội dung.
3. Paste vào ô Secrets của Streamlit.
4. Save.

## D. Deploy

Bấm Deploy.

Sau khi thành công, app có URL dạng:

```text
https://ten-app.streamlit.app
```

## E. Kiểm tra sau deploy

1. Mở URL bằng cửa sổ ẩn danh.
2. Nhập mã học sinh thử.
3. Làm 1 câu Thử thách.
4. Kiểm tra Google Sheet xuất hiện dòng mới.
5. Vào trang Dành cho GV bằng PIN.
6. Thử Pre-test bằng mã thử trước khi phát link chính thức.

## F. Cập nhật app

Sau khi sửa code và commit lên GitHub, Streamlit sẽ cập nhật app từ repository.
Nếu chưa thấy thay đổi, dùng Reboot app trong phần quản lý.

## Tài liệu chính thức

- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
