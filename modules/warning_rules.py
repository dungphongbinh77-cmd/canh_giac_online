import re

WARNING_PATTERNS = {
    "Yêu cầu OTP": [r"\botp\b", r"mã xác thực"],
    "Tạo áp lực thời gian": [r"ngay", r"gấp", r"trong \d+ phút", r"khẩn cấp", r"sắp bị khóa"],
    "Hứa hẹn lợi ích bất thường": [r"trúng thưởng", r"miễn phí", r"nhận quà", r"lợi nhuận", r"hoa hồng cao"],
    "Yêu cầu chuyển/nạp tiền": [r"chuyển tiền", r"nạp tiền", r"đóng phí", r"thanh toán phí"],
    "Yêu cầu thông tin nhạy cảm": [r"mật khẩu", r"số thẻ", r"cccd", r"thông tin cá nhân"],
    "Có dấu hiệu đường link": [r"http[s]?://", r"www\.", r"bit\.ly", r"bấm link", r"nhấn link", r"đường dẫn", r"liên kết"]
}

def find_warning_signs(text: str):
    text = text.lower()
    signs = []
    for label, patterns in WARNING_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                signs.append(label)
                break
    return signs

def education_advice(signs):
    advice = []
    if "Yêu cầu OTP" in signs or "Yêu cầu thông tin nhạy cảm" in signs:
        advice.append("Không cung cấp OTP, mật khẩu hoặc thông tin cá nhân.")
    if "Có dấu hiệu đường link" in signs:
        advice.append("Không bấm đường link lạ; hãy tự mở ứng dụng hoặc website chính thức.")
    if "Yêu cầu chuyển/nạp tiền" in signs:
        advice.append("Không chuyển tiền trước khi xác minh rõ danh tính và nguồn yêu cầu.")
    if "Tạo áp lực thời gian" in signs:
        advice.append("Không hành động vội vàng; dừng lại và kiểm tra bằng kênh khác.")
    if not advice:
        advice.append("Tiếp tục kiểm tra nguồn gửi và chỉ làm theo hướng dẫn từ kênh chính thức.")
    return advice
