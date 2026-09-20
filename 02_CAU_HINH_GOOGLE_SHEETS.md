# 02 - CẤU HÌNH GOOGLE SHEETS

## A. Tạo Google Sheet

1. Tạo một Google Sheet mới.
2. Đặt tên, ví dụ: `CANH_GIAC_ONLINE_DATA`.
3. Không cần tạo sheet con; app sẽ tự tạo:
   - `quiz_attempts`
   - `message_checks`
   - `research_responses`

## B. Lấy Spreadsheet ID

URL dạng:

```text
https://docs.google.com/spreadsheets/d/ABC123XYZ/edit
```

Spreadsheet ID là phần `ABC123XYZ`.

## C. Tạo Google Cloud Project + Service Account

1. Vào Google Cloud Console.
2. Tạo project mới.
3. Bật Google Sheets API và Google Drive API.
4. Tạo Service Account.
5. Tạo JSON key cho Service Account và tải file JSON về máy.

KHÔNG upload JSON này lên GitHub.

## D. Chia sẻ Google Sheet

Mở file JSON, lấy giá trị `client_email`.
Chia sẻ Google Sheet cho email này với quyền Editor.

## E. Tạo Secrets tự động

Ví dụ file JSON tên `service-account.json` nằm ngoài thư mục GitHub:

```bash
python tools/make_secrets.py --json "C:\duong-dan\service-account.json" --spreadsheet-id "ABC123XYZ" --admin-pin "PIN_GV_CUA_THAY_CO"
```

Script sẽ tạo:

```text
.streamlit/secrets.toml
```

Tệp này chỉ dùng cục bộ hoặc để copy nội dung lên Streamlit Cloud. Không commit lên GitHub.

## F. Kiểm tra cục bộ

Chạy:

```bash
python -m streamlit run app.py
```

Trong app, dòng kho dữ liệu cần hiện:

```text
Kho dữ liệu: Google Sheets
```

Vào `Dành cho GV` để kiểm tra kết nối.

## Tài liệu chính thức

- https://developers.google.com/workspace/guides/create-credentials
- https://developers.google.com/workspace/sheets/api/guides/concepts
