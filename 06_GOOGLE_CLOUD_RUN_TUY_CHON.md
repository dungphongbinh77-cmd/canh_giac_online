# 06 - TÙY CHỌN: HOST APP TRỰC TIẾP TRÊN GOOGLE CLOUD RUN

Phương án này dành cho Thầy/Cô muốn app thực sự chạy trên hạ tầng Google thay vì Streamlit Community Cloud.

## Lưu ý

- Khó hơn Streamlit Community Cloud.
- Cần Google Cloud Project; một số cấu hình có thể yêu cầu billing.
- Bộ dự án có `Dockerfile` sẵn.

## Triển khai cơ bản

Sau khi cài Google Cloud CLI và đăng nhập:

```bash
gcloud auth login
gcloud config set project PROJECT_ID
gcloud run deploy canh-giac-online --source . --region asia-southeast1 --allow-unauthenticated
```

Bản code trong bộ này ưu tiên Streamlit Secrets cho Google Sheets. Nếu dùng Cloud Run, cách đơn giản nhất vẫn là cung cấp Secrets an toàn qua cơ chế bí mật của Google Cloud hoặc cấu hình môi trường phù hợp trước khi dùng thật.

Nếu mục tiêu là triển khai nhanh cho HS, hãy dùng Streamlit Community Cloud + Google Sheets trước.
