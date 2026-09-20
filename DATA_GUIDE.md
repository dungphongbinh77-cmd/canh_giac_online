# Hướng dẫn bộ dữ liệu 800 mẫu

Bộ `data/messages.csv` gồm 800 thông điệp mô phỏng, cân bằng 400 mẫu nguy cơ và 400 mẫu bình thường.

## Các cột
- `id`: mã mẫu.
- `message`: nội dung thông điệp.
- `label`: 1 = nguy cơ; 0 = bình thường/an toàn.
- `category`: nhóm nội dung.
- `red_flags`: dấu hiệu dùng cho phần giải thích.
- `source_type`: nguồn dữ liệu. Phiên bản này là dữ liệu mô phỏng phục vụ nghiên cứu.
- `difficulty`: độ khó tương đối.
- `template_id`: mã họ câu chữ; các mẫu cùng họ không bị chia sang nhiều tập khác nhau.
- `split`: train / validation / test.

## 8 nhóm nguy cơ
- LD1_REWARD: trúng thưởng/quà tặng.
- LD2_ORG_IMPERSONATION: giả danh tổ chức.
- LD3_FRIEND_IMPERSONATION: giả danh người thân/bạn bè.
- LD4_OTP_PASSWORD: yêu cầu OTP/mật khẩu.
- LD5_SUSPICIOUS_LINK: đường link đáng ngờ.
- LD6_ACCOUNT_LOCK: đe dọa khóa tài khoản.
- LD7_JOB_INVESTMENT: việc làm/đầu tư nộp tiền trước.
- LD8_URGENCY_TRANSFER: tạo áp lực/chuyển tiền.

## 8 nhóm bình thường
- BT1_SCHOOL: thông báo trường/lớp.
- BT2_STUDY: học tập.
- BT3_FAMILY_FRIEND: gia đình/bạn bè.
- BT4_DIGITAL_SAFETY: nội dung giáo dục an toàn số, có các từ khóa như OTP/link nhưng không phải lừa đảo.
- BT5_OFFICIAL_ACCOUNT: thông báo tài khoản theo hướng an toàn/chính thức.
- BT6_ACTIVITY: hoạt động trường/lớp.
- BT7_PAYMENT_LEGIT: nội dung tiền bạc hợp lệ hoặc cảnh báo không chuyển tiền.
- BT8_GENERAL: thông điệp thông thường.

## Phân chia dữ liệu
- Train: 560 mẫu.
- Validation: 120 mẫu.
- Test: 120 mẫu.
- Mỗi tập đều cân bằng hai nhãn.
- Các mẫu cùng `template_id` chỉ nằm trong một split để giảm rò rỉ mẫu câu giữa train và test.

## Lưu ý nghiên cứu
Đây là dữ liệu mô phỏng để học sinh phát triển nguyên mẫu. Khi viết báo cáo KHKT chính thức cần rà soát thủ công, gán nhãn độc lập, bổ sung dữ liệu thực tế đã ẩn danh và ghi rõ nguồn/phương pháp thu thập. Không nên dùng độ chính xác từ bộ mô phỏng này làm bằng chứng duy nhất về hiệu quả ngoài thực tế.
