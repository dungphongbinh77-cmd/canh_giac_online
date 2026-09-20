from pathlib import Path
import random

import joblib
import pandas as pd
import streamlit as st

from modules.warning_rules import find_warning_signs, education_advice
from modules.storage import (
    init_db,
    normalize_student_code,
    valid_student_code,
    save_quiz_attempt,
    save_message_check,
    student_summary,
    category_stats,
    recent_attempts,
    export_student_attempts,
)

APP_VERSION = "Student v1.0"
ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "model" / "classifier.joblib"
QUIZ_PATH = ROOT / "data" / "situations.csv"
CODES_PATH = ROOT / "data" / "student_codes.csv"

st.set_page_config(
    page_title="Cảnh giác Online",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: .8rem; padding-bottom: 4rem; max-width: 760px;}
    h1 {font-size: 1.75rem !important; margin-bottom: .15rem !important;}
    h2, h3 {line-height: 1.25;}
    div.stButton > button {width: 100%; min-height: 3rem; font-weight: 700; border-radius: 12px;}
    div[data-baseweb="select"] > div {min-height: 3rem; border-radius: 12px;}
    textarea {font-size: 1rem !important;}
    .cg-card {padding: .9rem 1rem; border: 1px solid rgba(128,128,128,.25); border-radius: 14px; margin: .45rem 0;}
    .cg-note {font-size: .88rem; opacity: .82;}
    .cg-hero {padding: 1rem; border-radius: 16px; background: rgba(37,99,235,.07); margin-bottom: .75rem;}
    @media (max-width: 640px) {
      .block-container {padding-left: .75rem; padding-right: .75rem;}
      h1 {font-size: 1.5rem !important;}
      div[data-testid="stMetricValue"] {font-size: 1.4rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_quiz():
    df = pd.read_csv(QUIZ_PATH)
    if "question_id" not in df.columns:
        df.insert(0, "question_id", [f"Q{i+1:03d}" for i in range(len(df))])
    if "category" not in df.columns:
        df["category"] = "Tổng hợp"
    return df


@st.cache_data
def load_allowed_codes():
    if not CODES_PATH.exists():
        return set()
    df = pd.read_csv(CODES_PATH)
    if "student_code" not in df.columns:
        return set()
    if "active" in df.columns:
        active = pd.to_numeric(df["active"], errors="coerce").fillna(0).astype(int) == 1
        df = df[active]
    return {normalize_student_code(v) for v in df["student_code"].astype(str)}


def code_is_allowed(code: str) -> bool:
    codes = load_allowed_codes()
    return valid_student_code(code) and (not codes or code in codes)


if "student_code" not in st.session_state:
    st.session_state.student_code = ""

st.title("🛡️ CẢNH GIÁC ONLINE")
st.caption("Học cách nhận diện thông điệp đáng ngờ và bảo vệ mình trên môi trường số")

student_code = st.session_state.student_code

if not student_code:
    st.markdown(
        "<div class='cg-hero'><b>Chào em!</b><br>Nhập mã học sinh do giáo viên cấp để bắt đầu. Ứng dụng không yêu cầu họ tên.</div>",
        unsafe_allow_html=True,
    )
    raw_code = st.text_input(
        "Mã học sinh",
        placeholder="Ví dụ: HS001",
        max_chars=24,
    )
    cleaned_code = normalize_student_code(raw_code)
    if cleaned_code and cleaned_code != raw_code:
        st.caption(f"Mã sẽ được chuẩn hóa thành: {cleaned_code}")
    if st.button("BẮT ĐẦU", type="primary"):
        if code_is_allowed(cleaned_code):
            st.session_state.student_code = cleaned_code
            st.rerun()
        else:
            st.error("Mã chưa đúng hoặc chưa được kích hoạt. Hãy kiểm tra lại mã giáo viên đã cấp.")

    st.markdown("### Lưu ý an toàn")
    st.write("• Không nhập OTP thật, mật khẩu, số thẻ, số tài khoản hoặc thông tin bí mật vào ứng dụng.")
    st.write("• Khi kiểm tra thông điệp, ứng dụng không lưu nội dung em nhập; chỉ lưu kết quả phân tích để theo dõi học tập.")
    st.write("• Kết quả chỉ có tính hỗ trợ học tập. Khi nghi ngờ, hãy hỏi cha mẹ, giáo viên hoặc kiểm tra qua kênh chính thức.")
    st.stop()

st.markdown(
    f"<div class='cg-note'>Mã học sinh: <b>{student_code}</b> • {APP_VERSION}</div>",
    unsafe_allow_html=True,
)

with st.expander("Đổi mã học sinh"):
    st.caption("Chỉ đổi mã khi giáo viên yêu cầu.")
    if st.button("ĐỔI MÃ"):
        st.session_state.student_code = ""
        for key in ["quiz_index", "quiz_checked", "quiz_choice", "quiz_saved_key"]:
            st.session_state.pop(key, None)
        st.rerun()

page = st.selectbox(
    "Chức năng",
    ["🏠 Trang chủ", "🔎 Kiểm tra thông điệp", "🎮 Thử thách", "📈 Tiến bộ của tôi", "📚 An toàn số"],
    label_visibility="collapsed",
)

if page == "🏠 Trang chủ":
    st.subheader("🏠 Hôm nay em muốn làm gì?")
    st.markdown("<div class='cg-card'><b>🔎 Kiểm tra thông điệp</b><br>Phân tích một tin nhắn đáng ngờ và xem các dấu hiệu cảnh báo.</div>", unsafe_allow_html=True)
    st.markdown("<div class='cg-card'><b>🎮 Thử thách</b><br>Luyện cách xử lý các tình huống thường gặp trên mạng.</div>", unsafe_allow_html=True)
    st.markdown("<div class='cg-card'><b>📈 Tiến bộ của tôi</b><br>Xem số câu đã làm và những chủ đề cần luyện thêm.</div>", unsafe_allow_html=True)
    st.markdown("<div class='cg-card'><b>📚 An toàn số</b><br>Ghi nhớ các nguyên tắc giúp bảo vệ tài khoản và thông tin cá nhân.</div>", unsafe_allow_html=True)
    st.info("Quy tắc nhanh: DỪNG LẠI → KIỂM TRA → XÁC MINH → HỎI NGƯỜI LỚN → MỚI HÀNH ĐỘNG")

elif page == "🔎 Kiểm tra thông điệp":
    st.subheader("🔎 Kiểm tra thông điệp")
    st.warning("Không dán OTP thật, mật khẩu, số thẻ, số tài khoản hoặc thông tin bí mật.")
    text = st.text_area(
        "Nhập hoặc dán nội dung cần kiểm tra:",
        height=170,
        placeholder="Ví dụ: Tài khoản của bạn sẽ bị khóa trong 10 phút. Hãy bấm link...",
    )

    if st.button("PHÂN TÍCH", type="primary"):
        if not text.strip():
            st.warning("Hãy nhập nội dung cần kiểm tra.")
        elif not MODEL_PATH.exists():
            st.error("Ứng dụng đang thiếu mô hình phân tích. Hãy báo giáo viên.")
        else:
            model = load_model()
            score = round(float(model.predict_proba([text])[0][1]) * 100, 1)

            if score >= 70:
                level, view = "Nguy cơ cao", "🔴 NGUY CƠ CAO"
            elif score >= 40:
                level, view = "Cần thận trọng", "🟡 CẦN THẬN TRỌNG"
            else:
                level, view = "Nguy cơ thấp", "🟢 NGUY CƠ THẤP"

            signs = find_warning_signs(text)
            advice = education_advice(signs)
            save_message_check(student_code, score, level, signs)

            st.metric("Điểm nguy cơ do mô hình ước lượng", f"{score}%")
            st.markdown(f"### {view}")
            st.markdown("**Dấu hiệu phát hiện**")
            if signs:
                for item in signs:
                    st.markdown(f"<div class='cg-card'>✓ {item}</div>", unsafe_allow_html=True)
            else:
                st.write("Chưa phát hiện quy tắc cảnh báo nổi bật.")

            st.markdown("**Em nên làm gì?**")
            for item in advice:
                st.write("•", item)

            st.info("Ứng dụng không lưu nội dung tin nhắn em vừa nhập. Kết quả không thay thế việc xác minh qua nguồn chính thức.")

elif page == "🎮 Thử thách":
    st.subheader("🎮 Thử thách an toàn số")
    quiz = load_quiz()
    categories = ["Tất cả"] + sorted(quiz["category"].dropna().astype(str).unique().tolist())
    selected_category = st.selectbox("Chủ đề luyện tập", categories)
    filtered = quiz if selected_category == "Tất cả" else quiz[quiz["category"].astype(str) == selected_category]
    filtered = filtered.reset_index(drop=True)

    if "quiz_index" not in st.session_state or st.session_state.quiz_index >= len(filtered):
        st.session_state.quiz_index = random.randrange(len(filtered))
        st.session_state.quiz_checked = False
        st.session_state.quiz_choice = "A"
        st.session_state.quiz_saved_key = ""

    row = filtered.iloc[st.session_state.quiz_index]
    question_key = f"{row['question_id']}::{selected_category}"
    st.caption(f"Chủ đề: {row['category']} • Câu {row['question_id']}")
    st.markdown(f"### {row['question']}")

    choice = st.radio(
        "Chọn phương án:",
        ["A", "B", "C", "D"],
        index=["A", "B", "C", "D"].index(st.session_state.get("quiz_choice", "A")),
        format_func=lambda x: f"{x}. {row[x]}",
        key=f"quiz_radio_{row['question_id']}_{selected_category}",
    )
    st.session_state.quiz_choice = choice

    if st.button("KIỂM TRA ĐÁP ÁN", type="primary"):
        st.session_state.quiz_checked = True
        if st.session_state.get("quiz_saved_key") != question_key:
            save_quiz_attempt(
                student_code=student_code,
                question_id=row["question_id"],
                category=row["category"],
                selected_answer=choice,
                correct_answer=row["answer"],
            )
            st.session_state.quiz_saved_key = question_key

    if st.session_state.quiz_checked:
        if choice == row["answer"]:
            st.success("✅ Chính xác!")
        else:
            st.error(f"Chưa đúng. Đáp án phù hợp là {row['answer']}.")
        st.markdown(f"**Vì sao?** {row['explanation']}")

        if st.button("CÂU TIẾP THEO"):
            old = st.session_state.quiz_index
            if len(filtered) > 1:
                while st.session_state.quiz_index == old:
                    st.session_state.quiz_index = random.randrange(len(filtered))
            st.session_state.quiz_checked = False
            st.session_state.quiz_choice = "A"
            st.session_state.quiz_saved_key = ""
            st.rerun()

elif page == "📈 Tiến bộ của tôi":
    st.subheader("📈 Tiến bộ của tôi")
    summary = student_summary(student_code)
    c1, c2 = st.columns(2)
    c1.metric("Lượt luyện tập", summary["attempts"])
    c2.metric("Câu đúng", summary["correct"])
    c3, c4 = st.columns(2)
    c3.metric("Tỷ lệ đúng", f"{summary['accuracy']:.1f}%")
    c4.metric("Lượt kiểm tra tin", summary["checks"])

    if summary["attempts"] >= 20 and summary["accuracy"] >= 80:
        st.success("🏅 Huy hiệu: Chiến binh An toàn số")
    elif summary["attempts"] >= 10:
        st.info("⭐ Em đang tiến bộ tốt. Hãy tiếp tục luyện thêm các chủ đề còn yếu.")

    stats = category_stats(student_code)
    if stats:
        st.markdown("**Kết quả theo chủ đề**")
        df = pd.DataFrame(stats)
        st.bar_chart(df.set_index("category")[["accuracy"]], y="accuracy", y_label="Tỷ lệ đúng (%)")
        st.dataframe(
            df.rename(columns={"category": "Chủ đề", "attempts": "Số lượt", "correct": "Số đúng", "accuracy": "Tỷ lệ đúng (%)"}),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Em chưa có dữ liệu luyện tập. Hãy thử một vài câu ở mục Thử thách.")

    history = recent_attempts(student_code, 10)
    if history:
        st.markdown("**10 lượt gần nhất**")
        hist = pd.DataFrame(history)
        hist["Kết quả"] = pd.to_numeric(hist["is_correct"], errors="coerce").fillna(0).astype(int).map({1: "Đúng", 0: "Sai"})
        hist = hist.rename(columns={
            "question_id": "Câu", "category": "Chủ đề", "selected_answer": "Đã chọn",
            "correct_answer": "Đáp án", "created_at": "Thời gian"
        })[["Câu", "Chủ đề", "Đã chọn", "Đáp án", "Kết quả", "Thời gian"]]
        st.dataframe(hist, use_container_width=True, hide_index=True)

    rows = export_student_attempts(student_code)
    if rows:
        csv_bytes = pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "TẢI KẾT QUẢ CỦA TÔI",
            data=csv_bytes,
            file_name=f"ket_qua_{student_code}.csv",
            mime="text/csv",
            use_container_width=True,
        )

elif page == "📚 An toàn số":
    st.subheader("📚 5 nguyên tắc an toàn")
    principles = [
        ("1", "Không chia sẻ OTP/mật khẩu", "Không cung cấp OTP, mật khẩu hoặc mã xác thực cho người khác."),
        ("2", "Không bấm link lạ", "Tự mở ứng dụng hoặc website chính thức để kiểm tra thông tin."),
        ("3", "Không vội chuyển tiền", "Đặc biệt thận trọng khi người gửi tạo cảm giác khẩn cấp hoặc thúc giục."),
        ("4", "Xác minh bằng kênh khác", "Gọi điện, gặp trực tiếp hoặc dùng kênh chính thức để xác minh danh tính."),
        ("5", "Hỏi người lớn khi chưa chắc", "Trao đổi với cha mẹ, giáo viên hoặc người lớn đáng tin cậy."),
    ]
    for num, title, desc in principles:
        st.markdown(f"<div class='cg-card'><b>{num}. {title}</b><br>{desc}</div>", unsafe_allow_html=True)
    st.markdown("### Quy tắc 5 bước")
    st.info("DỪNG LẠI → KIỂM TRA → XÁC MINH → HỎI NGƯỜI LỚN → MỚI HÀNH ĐỘNG")
