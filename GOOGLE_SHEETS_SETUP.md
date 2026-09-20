# CAU HINH GOOGLE SHEETS CHO CANH GIAC ONLINE

## Muc tieu
Luu ket qua hoc sinh tap trung tren Google Sheets khi ung dung chay tren Streamlit Community Cloud.

## 1. Tao Google Sheet
Tao mot bang tinh moi, vi du: `CANH_GIAC_ONLINE_DATA`.
Khong can tao san cac trang tinh. App se tao `quiz_attempts` va `message_checks` khi ket noi thanh cong.

Lay `spreadsheet_id` trong URL:
`https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`

## 2. Tao Google Cloud project
Truy cap Google Cloud Console, tao project moi.
Bat hai API:
- Google Sheets API
- Google Drive API

## 3. Tao Service Account
Trong Google Cloud Console:
IAM & Admin / Service Accounts -> Create service account.
Sau do tao JSON key va tai file JSON ve may.

TUYET DOI KHONG upload file JSON nay len GitHub.

## 4. Chia se Google Sheet cho Service Account
Mo file JSON, tim truong `client_email`, co dang:
`ten-service-account@ten-project.iam.gserviceaccount.com`

Mo Google Sheet -> Share -> them email nay -> quyen Editor.
Service Account khong co hop thu, khong can gui thong bao.

## 5. Cau hinh Streamlit Secrets
Mo `.streamlit/secrets.toml.example` de xem mau.

Tren Streamlit Community Cloud:
App -> Settings -> Secrets -> paste:
- spreadsheet_id
- admin_pin
- toan bo phan [gcp_service_account] tu JSON service account

Khong commit secrets.toml len GitHub.

## 6. Kiem tra
Mo app -> muc `Danh cho GV` -> Kiem tra ket noi.
Neu thanh cong, Google Sheet se co hai tab:
- quiz_attempts
- message_checks

## 7. Du lieu luu
`quiz_attempts` luu: ma hoc sinh, cau hoi, chu de, lua chon, dap an, dung/sai, thoi gian.
`message_checks` luu: ma hoc sinh, diem nguy co, muc canh bao, dau hieu, thoi gian.

Khong luu ho ten that, so dien thoai, OTP hoac mat khau.
