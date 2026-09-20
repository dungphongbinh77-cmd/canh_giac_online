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
    storage_mode,
    storage_health,
    teacher_summary,
    export_all_quiz_attempts,
    export_all_message_checks,
    has_completed_test, save_research_test, student_research_summary,
    research_teacher_summary, export_research_responses,
)

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "model" / "classifier.joblib"
QUIZ_PATH = ROOT / "data" / "situations.csv"
PRETEST_PATH = ROOT / "data" / "pretest.csv"
POSTTEST_PATH = ROOT / "data" / "posttest.csv"
STUDENTS_PATH = ROOT / "data" / "students.csv"

st.set_page_config(
    page_title="Cảnh giác Online",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Tối ưu hiển thị trên điện thoại.
st.markdown(
    """
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 4rem; max-width: 760px;}
    h1 {font-size: 1.85rem !important; margin-bottom: .2rem !important;}
    h2, h3 {line-height: 1.25;}
    div.stButton > button {width: 100%; min-height: 3rem; font-weight: 700; border-radius: 12px;}
    div[data-baseweb="select"] > div {min-height: 3rem; border-radius: 12px;}
    textarea {font-size: 1rem !important;}
    .cg-card {padding: 0.9rem 1rem; border: 1px solid rgba(128,128,128,.25); border-radius: 14px; margin: .45rem 0;}
    .cg-note {font-size: .88rem; opacity: .82;}
    @media (max-width: 640px) {
      .block-container {padding-left: .8rem; padding-right: .8rem;}
      h1 {font-size: 1.55rem !important;}
      div[data-testid="stMetricValue"] {font-size: 1.45rem;}
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
def load_research_test(test_type: str):
    path = PRETEST_PATH if test_type == "PRE" else POSTTEST_PATH
    return pd.read_csv(path)


@st.cache_data
def load_students():
    return pd.read_csv(STUDENTS_PATH)


def research_group_for(code: str):
    df = load_students()
    m = df[df["student_code"].astype(str).str.upper() == str(code).upper()]
    if m.empty:
        return None
    return str(m.iloc[0]["group"])


if "student_code" not in st.session_state:
    st.session_state.student_code = ""

st.title("🛡️ CẢNH GIÁC ONLINE")
st.caption("Nhận diện dấu hiệu đáng ngờ • Luyện kỹ năng an toàn số • Theo dõi tiến bộ")
st.caption(f"💾 Kho dữ liệu: {storage_mode()}")

with st.expander("👤 Mã học sinh", expanded=not bool(st.session_state.student_code)):
    raw_code = st.text_input(
        "Nhập mã học sinh (không dùng họ tên, số điện thoại):",
        value=st.session_state.student_code,
        placeholder="Ví dụ: 9A_HS01",
        max_chars=24,
    )
    cleaned_code = normalize_student_code(raw_code)
    if cleaned_code and cleaned_code != raw_code:
        st.caption(f"Mã sẽ được chuẩn hóa thành: {cleaned_code}")
    if st.button("SỬ DỤNG MÃ NÀY"):
        if valid_student_code(cleaned_code):
            st.session_state.student_code = cleaned_code
            st.success(f"Đang sử dụng mã: {cleaned_code}")
            st.rerun()
        else:
            st.warning("Mã cần từ 3–24 ký tự, chỉ dùng chữ, số, dấu _ hoặc -.")

student_code = st.session_state.student_code
if student_code:
    st.markdown(f"<div class='cg-note'>Mã đang dùng: <b>{student_code}</b></div>", unsafe_allow_html=True)
else:
    st.info("Có thể xem ứng dụng ngay. Hãy nhập mã học sinh nếu muốn lưu tiến bộ.")

page = st.selectbox(
    "Chọn chức năng",
    ["🔎 Kiểm tra thông điệp", "🎮 Thử thách", "🧪 Nghiên cứu", "📈 Tiến bộ của tôi", "📚 Góc an toàn số", "📊 Dành cho GV"],
    label_visibility="collapsed",
)

if page == "🔎 Kiểm tra thông điệp":
    st.subheader("🔎 Kiểm tra thông điệp")
    text = st.text_area(
        "Nhập hoặc dán nội dung tin nhắn:",
        height=170,
        placeholder="Ví dụ: Tài khoản của bạn sẽ bị khóa trong 10 phút. Hãy bấm link...",
    )

    if st.button("PHÂN TÍCH THÔNG ĐIỆP", type="primary"):
        if not text.strip():
            st.warning("Hãy nhập nội dung cần kiểm tra.")
        elif not MODEL_PATH.exists():
            st.error("Chưa có mô hình. Hãy chạy: python model/train.py")
        else:
            model = load_model()
            proba = float(model.predict_proba([text])[0][1])
            score = round(proba * 100, 1)

            if score >= 70:
                level = "Nguy cơ cao"
                level_view = "🔴 NGUY CƠ CAO"
            elif score >= 40:
                level = "Cần thận trọng"
                level_view = "🟡 CẦN THẬN TRỌNG"
            else:
                level = "Nguy cơ thấp"
                level_view = "🟢 NGUY CƠ THẤP"

            signs = find_warning_signs(text)
            advice = education_advice(signs)

            if student_code:
                save_message_check(student_code, score, level, signs)

            st.metric("Điểm nguy cơ do mô hình ước lượng", f"{score}%")
            st.markdown(f"### {level_view}")

            st.markdown("**Dấu hiệu hệ thống phát hiện**")
            if signs:
                for s in signs:
                    st.markdown(f"<div class='cg-card'>✓ {s}</div>", unsafe_allow_html=True)
            else:
                st.write("Chưa phát hiện quy tắc cảnh báo nổi bật.")

            st.markdown("**Khuyến nghị**")
            for item in advice:
                st.write("•", item)

            st.info(
                "Đây là công cụ hỗ trợ học tập, không phải kết luận chắc chắn. "
                "Khi có nghi ngờ, hãy xác minh qua cha mẹ, giáo viên hoặc kênh chính thức."
            )

elif page == "🎮 Thử thách":
    st.subheader("🎮 Bạn sẽ làm gì?")
    quiz = load_quiz()

    if "quiz_index" not in st.session_state:
        st.session_state.quiz_index = random.randrange(len(quiz))
        st.session_state.quiz_checked = False
        st.session_state.quiz_choice = "A"

    row = quiz.iloc[st.session_state.quiz_index]
    st.caption(f"Chủ đề: {row['category']} • Câu: {row['question_id']}")
    st.markdown(f"### {row['question']}")

    choice = st.radio(
        "Chọn phương án:",
        ["A", "B", "C", "D"],
        index=["A", "B", "C", "D"].index(st.session_state.get("quiz_choice", "A")),
        format_func=lambda x: f"{x}. {row[x]}",
        key="quiz_radio",
    )
    st.session_state.quiz_choice = choice

    if st.button("KIỂM TRA ĐÁP ÁN", type="primary"):
        st.session_state.quiz_checked = True
        if student_code:
            save_quiz_attempt(
                student_code=student_code,
                question_id=row["question_id"],
                category=row["category"],
                selected_answer=choice,
                correct_answer=row["answer"],
            )

    if st.session_state.quiz_checked:
        if choice == row["answer"]:
            st.success("✅ Chính xác!")
        else:
            st.error(f"Chưa đúng. Đáp án phù hợp là {row['answer']}.")
        st.markdown(f"**Giải thích:** {row['explanation']}")
        if not student_code:
            st.caption("Nhập mã học sinh ở đầu trang nếu muốn lưu kết quả này.")

        if st.button("CÂU TIẾP THEO"):
            old = st.session_state.quiz_index
            if len(quiz) > 1:
                while st.session_state.quiz_index == old:
                    st.session_state.quiz_index = random.randrange(len(quiz))
            st.session_state.quiz_checked = False
            st.session_state.quiz_choice = "A"
            if "quiz_radio" in st.session_state:
                del st.session_state["quiz_radio"]
            st.rerun()

elif page == "🧪 Nghiên cứu":
    st.subheader("🧪 Pre-test / Post-test")
    st.info(
        "Phần này dùng cho thực nghiệm nghiên cứu. Trong lúc làm bài, hệ thống không hiển thị đáp án đúng "
        "để tránh ảnh hưởng đến kết quả nghiên cứu."
    )
    if not student_code:
        st.warning("Hãy nhập mã học sinh ở đầu trang trước khi làm bài nghiên cứu.")
    else:
        group_name = research_group_for(student_code)
        if not group_name:
            st.error("Mã này chưa có trong data/students.csv. Hãy dùng mã nghiên cứu do giáo viên cấp.")
        else:
            st.caption(f"Nhóm nghiên cứu: {group_name}")
            test_label = st.radio("Chọn bài", ["Pre-test", "Post-test"], horizontal=True)
            test_type = "PRE" if test_label == "Pre-test" else "POST"
            completed = has_completed_test(student_code, test_type)
            if completed:
                sm = student_research_summary(student_code)
                s = sm[test_type]
                st.success(f"Mã {student_code} đã hoàn thành {test_label}.")
                if s:
                    st.metric("Điểm đã ghi nhận", f"{s['score']}/{s['total']}")
                st.caption("Muốn làm lại vì lý do kỹ thuật, giáo viên cần xóa lượt cũ trong kho dữ liệu trước.")
            else:
                test_df = load_research_test(test_type)
                state_key = f"research_answers_{test_type}"
                if state_key not in st.session_state:
                    st.session_state[state_key] = {}
                answers = st.session_state[state_key]

                st.progress(len(answers) / len(test_df))
                st.caption(f"Đã trả lời {len(answers)}/{len(test_df)} câu")
                for idx, row in test_df.iterrows():
                    qid = str(row["question_id"])
                    with st.expander(f"Câu {idx+1}. {row['question']}", expanded=(idx == len(answers))):
                        current = answers.get(qid)
                        options = ["A","B","C","D"]
                        selection = st.radio(
                            "Chọn đáp án",
                            options,
                            index=options.index(current) if current in options else None,
                            format_func=lambda x, r=row: f"{x}. {r[x]}",
                            key=f"{test_type}_{qid}",
                        )
                        if selection:
                            answers[qid] = selection

                st.session_state[state_key] = answers
                if len(answers) < len(test_df):
                    st.warning("Hãy trả lời đủ 20 câu trước khi nộp bài.")
                if st.button(f"NỘP {test_label.upper()}", type="primary", disabled=len(answers) < len(test_df)):
                    responses=[]
                    for _, row in test_df.iterrows():
                        qid=str(row["question_id"])
                        responses.append({
                            "question_id": qid,
                            "construct": row["construct"],
                            "selected_answer": answers[qid],
                            "correct_answer": row["answer"],
                        })
                    save_research_test(student_code, group_name, test_type, responses)
                    st.session_state.pop(state_key, None)
                    for qid in test_df["question_id"].astype(str):
                        st.session_state.pop(f"{test_type}_{qid}", None)
                    st.success("Đã ghi nhận bài. Cảm ơn em đã hoàn thành.")
                    st.rerun()

elif page == "📈 Tiến bộ của tôi":
    st.subheader("📈 Tiến bộ của tôi")
    if not student_code:
        st.warning("Hãy nhập mã học sinh ở đầu trang để xem tiến bộ.")
    else:
        summary = student_summary(student_code)
        c1, c2 = st.columns(2)
        c1.metric("Lượt làm câu hỏi", summary["attempts"])
        c2.metric("Số câu đúng", summary["correct"])
        c3, c4 = st.columns(2)
        c3.metric("Tỷ lệ đúng", f"{summary['accuracy']:.1f}%")
        c4.metric("Lượt kiểm tra tin", summary["checks"])

        stats = category_stats(student_code)
        if stats:
            st.markdown("**Kết quả theo chủ đề**")
            chart_df = pd.DataFrame(stats).set_index("category")[["accuracy"]]
            st.bar_chart(chart_df, y="accuracy", y_label="Tỷ lệ đúng (%)")
            st.dataframe(
                pd.DataFrame(stats).rename(
                    columns={
                        "category": "Chủ đề",
                        "attempts": "Số lượt",
                        "correct": "Số đúng",
                        "accuracy": "Tỷ lệ đúng (%)",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Chưa có dữ liệu luyện tập. Hãy làm một vài câu ở mục Thử thách.")

        history = recent_attempts(student_code, 10)
        if history:
            st.markdown("**10 lượt gần nhất**")
            hist_df = pd.DataFrame(history)
            hist_df["Kết quả"] = hist_df["is_correct"].map({1: "Đúng", 0: "Sai"})
            hist_df = hist_df.rename(
                columns={
                    "question_id": "Câu",
                    "category": "Chủ đề",
                    "selected_answer": "Đã chọn",
                    "correct_answer": "Đáp án",
                    "created_at": "Thời gian",
                }
            )[["Câu", "Chủ đề", "Đã chọn", "Đáp án", "Kết quả", "Thời gian"]]
            st.dataframe(hist_df, use_container_width=True, hide_index=True)

        all_rows = export_student_attempts(student_code)
        if all_rows:
            csv_bytes = pd.DataFrame(all_rows).to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "TẢI KẾT QUẢ CỦA TÔI (.CSV)",
                data=csv_bytes,
                file_name=f"ket_qua_{student_code}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        if storage_mode() == "Google Sheets":
            st.success("Kết quả của mã học sinh này đang được lưu tập trung trên Google Sheets.")
        else:
            st.caption(
                "Hiện app đang dùng SQLite cục bộ. Trên Streamlit Community Cloud, hãy cấu hình Google Sheets "
                "theo file GOOGLE_SHEETS_SETUP.md để lưu dữ liệu bền vững."
            )

elif page == "📊 Dành cho GV":
    st.subheader("📊 Dành cho giáo viên")
    ok, msg = storage_health()
    if ok:
        st.success(msg)
    else:
        st.error(msg)

    try:
        admin_pin = str(st.secrets.get("admin_pin", ""))
    except Exception:
        admin_pin = ""

    if not admin_pin:
        st.info("Chưa cấu hình admin_pin trong Streamlit Secrets. Trang này chưa mở thống kê toàn lớp.")
    else:
        entered_pin = st.text_input("Mã PIN giáo viên", type="password")
        if entered_pin == admin_pin:
            report = teacher_summary()
            c1, c2 = st.columns(2)
            c1.metric("Số mã học sinh", report["students"])
            c2.metric("Lượt luyện tập", report["quiz_attempts"])
            c3, c4 = st.columns(2)
            c3.metric("Tỷ lệ đúng chung", f'{report["accuracy"]:.1f}%')
            c4.metric("Lượt kiểm tra tin", report["message_checks"])

            if report["category_stats"]:
                st.markdown("**Kết quả theo chủ đề**")
                category_df = pd.DataFrame(report["category_stats"])
                st.bar_chart(category_df.set_index("category")[["accuracy"]], y="accuracy")
                st.dataframe(
                    category_df.rename(columns={
                        "category": "Chủ đề", "attempts": "Số lượt",
                        "correct": "Số đúng", "accuracy": "Tỷ lệ đúng (%)"
                    }),
                    use_container_width=True, hide_index=True,
                )

            if report["student_stats"]:
                st.markdown("**Theo mã học sinh**")
                student_df = pd.DataFrame(report["student_stats"])
                st.dataframe(
                    student_df.rename(columns={
                        "student_code": "Mã HS", "attempts": "Số lượt",
                        "correct": "Số đúng", "accuracy": "Tỷ lệ đúng (%)"
                    }),
                    use_container_width=True, hide_index=True,
                )


            research_report = research_teacher_summary()
            st.markdown("---")
            st.markdown("### 🧪 Kết quả Pre-test / Post-test")
            if research_report["scores"]:
                score_df = pd.DataFrame(research_report["scores"])
                st.dataframe(
                    score_df.rename(columns={"student_code":"Mã HS","group":"Nhóm","test_type":"Bài","score":"Điểm","total":"Tổng","percent":"Tỷ lệ (%)"}),
                    use_container_width=True, hide_index=True,
                )
                group_df = pd.DataFrame(research_report["group_summary"])
                st.markdown("**Trung bình theo nhóm**")
                st.dataframe(
                    group_df.rename(columns={"group":"Nhóm","test_type":"Bài","n":"Số HS","mean_score":"Điểm TB","mean_percent":"Tỷ lệ TB (%)"}),
                    use_container_width=True, hide_index=True,
                )
                pivot = group_df.pivot(index="group", columns="test_type", values="mean_score") if not group_df.empty else pd.DataFrame()
                if not pivot.empty:
                    st.bar_chart(pivot)
                research_all = export_research_responses()
                st.download_button(
                    "TẢI DỮ LIỆU PRE/POST (.CSV)",
                    data=research_all.to_csv(index=False).encode("utf-8-sig"),
                    file_name="canh_giac_online_pre_post.csv",
                    mime="text/csv", use_container_width=True,
                )
            else:
                st.info("Chưa có dữ liệu Pre-test/Post-test.")

            quiz_all = export_all_quiz_attempts()
            checks_all = export_all_message_checks()
            if not quiz_all.empty:
                st.download_button(
                    "TẢI TOÀN BỘ KẾT QUẢ LUYỆN TẬP (.CSV)",
                    data=quiz_all.to_csv(index=False).encode("utf-8-sig"),
                    file_name="canh_giac_online_quiz_attempts.csv",
                    mime="text/csv", use_container_width=True,
                )
            if not checks_all.empty:
                st.download_button(
                    "TẢI TOÀN BỘ LƯỢT KIỂM TRA TIN (.CSV)",
                    data=checks_all.to_csv(index=False).encode("utf-8-sig"),
                    file_name="canh_giac_online_message_checks.csv",
                    mime="text/csv", use_container_width=True,
                )
        elif entered_pin:
            st.error("Mã PIN chưa đúng.")

elif page == "📚 Góc an toàn số":
    st.subheader("📚 5 nguyên tắc an toàn")
    principles = [
        ("1", "Không chia sẻ OTP/mật khẩu", "Không cung cấp OTP, mật khẩu hoặc mã xác thực cho người khác."),
        ("2", "Không bấm link lạ", "Tự mở ứng dụng hoặc website chính thức để kiểm tra thông tin."),
        ("3", "Không vội chuyển tiền", "Đặc biệt thận trọng khi người gửi tạo cảm giác khẩn cấp hoặc thúc giục."),
        ("4", "Xác minh bằng kênh khác", "Gọi điện, gặp trực tiếp hoặc dùng kênh chính thức để xác minh danh tính."),
        ("5", "Hỏi người lớn khi chưa chắc", "Trao đổi với cha mẹ, giáo viên hoặc người lớn đáng tin cậy."),
    ]
    for num, title, desc in principles:
        st.markdown(
            f"<div class='cg-card'><b>{num}. {title}</b><br>{desc}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("### Khi gặp tin nhắn đáng ngờ")
    st.write("**DỪNG LẠI → KIỂM TRA → XÁC MINH → HỎI NGƯỜI LỚN → MỚI HÀNH ĐỘNG**")
