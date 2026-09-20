from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "progress.db"

QUIZ_HEADERS = [
    "student_code", "question_id", "category", "selected_answer",
    "correct_answer", "is_correct", "created_at"
]
CHECK_HEADERS = [
    "student_code", "risk_score", "risk_level", "warning_signs", "created_at"
]


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def normalize_student_code(raw: str) -> str:
    raw = (raw or "").strip().upper()
    raw = re.sub(r"[^A-Z0-9_-]", "", raw)
    return raw[:24]


def valid_student_code(code: str) -> bool:
    return 3 <= len(code) <= 24


# ---------- SQLite fallback ----------

def _connect_sqlite():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _init_sqlite():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect_sqlite() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_code TEXT NOT NULL,
                question_id TEXT NOT NULL,
                category TEXT,
                selected_answer TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS message_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_code TEXT NOT NULL,
                risk_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                warning_signs TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _sqlite_quiz_df() -> pd.DataFrame:
    with _connect_sqlite() as conn:
        return pd.read_sql_query(
            "SELECT student_code, question_id, category, selected_answer, correct_answer, is_correct, created_at FROM quiz_attempts",
            conn,
        )


def _sqlite_checks_df() -> pd.DataFrame:
    with _connect_sqlite() as conn:
        return pd.read_sql_query(
            "SELECT student_code, risk_score, risk_level, warning_signs, created_at FROM message_checks",
            conn,
        )


# ---------- Google Sheets ----------

def _get_streamlit_secrets():
    try:
        import streamlit as st
        return st.secrets
    except Exception:
        return {}


def _google_configured() -> bool:
    try:
        secrets = _get_streamlit_secrets()
        return bool(secrets.get("spreadsheet_id")) and "gcp_service_account" in secrets
    except Exception:
        return False


def _google_client():
    import gspread
    from google.oauth2.service_account import Credentials

    secrets = _get_streamlit_secrets()
    info = dict(secrets["gcp_service_account"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(credentials)


def _google_book():
    secrets = _get_streamlit_secrets()
    return _google_client().open_by_key(str(secrets["spreadsheet_id"]))


def _ensure_worksheet(book, title: str, headers: list[str]):
    try:
        ws = book.worksheet(title)
    except Exception:
        ws = book.add_worksheet(title=title, rows=3000, cols=max(10, len(headers)))
    if not ws.row_values(1):
        ws.append_row(headers, value_input_option="RAW")
    return ws


def _google_quiz_ws():
    return _ensure_worksheet(_google_book(), "quiz_attempts", QUIZ_HEADERS)


def _google_checks_ws():
    return _ensure_worksheet(_google_book(), "message_checks", CHECK_HEADERS)


def _worksheet_df(ws, headers: list[str]) -> pd.DataFrame:
    records = ws.get_all_records(expected_headers=headers)
    if not records:
        return pd.DataFrame(columns=headers)
    df = pd.DataFrame(records)
    for col in headers:
        if col not in df.columns:
            df[col] = ""
    return df[headers]


def _google_quiz_df() -> pd.DataFrame:
    return _worksheet_df(_google_quiz_ws(), QUIZ_HEADERS)


def _google_checks_df() -> pd.DataFrame:
    return _worksheet_df(_google_checks_ws(), CHECK_HEADERS)


# ---------- Public API ----------

def init_db():
    _init_sqlite()


def storage_ready() -> bool:
    if not _google_configured():
        return False
    try:
        book = _google_book()
        _ensure_worksheet(book, "quiz_attempts", QUIZ_HEADERS)
        _ensure_worksheet(book, "message_checks", CHECK_HEADERS)
        return True
    except Exception:
        return False


def save_quiz_attempt(student_code: str, question_id: str, category: str, selected_answer: str, correct_answer: str) -> str:
    row = [
        student_code, str(question_id), category, selected_answer,
        correct_answer, int(selected_answer == correct_answer), _now()
    ]
    if _google_configured():
        try:
            _google_quiz_ws().append_row(row, value_input_option="RAW")
            return "google"
        except Exception:
            pass

    with _connect_sqlite() as conn:
        conn.execute(
            "INSERT INTO quiz_attempts (student_code, question_id, category, selected_answer, correct_answer, is_correct, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            tuple(row),
        )
        conn.commit()
    return "local"


def save_message_check(student_code: str, risk_score: float, risk_level: str, warning_signs: list[str]) -> str:
    # Không lưu nội dung tin nhắn; chỉ lưu kết quả phân tích phục vụ theo dõi học tập.
    row = [student_code, float(risk_score), risk_level, "; ".join(warning_signs), _now()]
    if _google_configured():
        try:
            _google_checks_ws().append_row(row, value_input_option="RAW")
            return "google"
        except Exception:
            pass

    with _connect_sqlite() as conn:
        conn.execute(
            "INSERT INTO message_checks (student_code, risk_score, risk_level, warning_signs, created_at) VALUES (?, ?, ?, ?, ?)",
            tuple(row),
        )
        conn.commit()
    return "local"


def _quiz_df() -> pd.DataFrame:
    if _google_configured():
        try:
            return _google_quiz_df()
        except Exception:
            pass
    return _sqlite_quiz_df()


def _checks_df() -> pd.DataFrame:
    if _google_configured():
        try:
            return _google_checks_df()
        except Exception:
            pass
    return _sqlite_checks_df()


def student_summary(student_code: str) -> dict:
    quiz = _quiz_df()
    checks = _checks_df()
    q = quiz[quiz["student_code"].astype(str) == student_code].copy() if not quiz.empty else quiz
    c = checks[checks["student_code"].astype(str) == student_code].copy() if not checks.empty else checks
    attempts = len(q)
    correct = int(pd.to_numeric(q["is_correct"], errors="coerce").fillna(0).astype(int).sum()) if attempts else 0
    return {
        "attempts": int(attempts),
        "correct": correct,
        "accuracy": float(correct / attempts * 100) if attempts else 0.0,
        "checks": int(len(c)),
    }


def category_stats(student_code: str) -> list[dict]:
    quiz = _quiz_df()
    if quiz.empty:
        return []
    q = quiz[quiz["student_code"].astype(str) == student_code].copy()
    if q.empty:
        return []
    q["is_correct"] = pd.to_numeric(q["is_correct"], errors="coerce").fillna(0).astype(int)
    out = []
    for category, group in q.groupby("category", dropna=False):
        attempts = len(group)
        correct = int(group["is_correct"].sum())
        out.append({
            "category": str(category) if str(category) else "Khác",
            "attempts": attempts,
            "correct": correct,
            "accuracy": round(correct / attempts * 100, 1) if attempts else 0.0,
        })
    return sorted(out, key=lambda x: x["category"])


def recent_attempts(student_code: str, limit: int = 10) -> list[dict]:
    quiz = _quiz_df()
    if quiz.empty:
        return []
    q = quiz[quiz["student_code"].astype(str) == student_code].copy()
    if q.empty:
        return []
    q = q.sort_values("created_at", ascending=False).head(int(limit))
    return q.to_dict("records")


def export_student_attempts(student_code: str) -> list[dict]:
    quiz = _quiz_df()
    if quiz.empty:
        return []
    q = quiz[quiz["student_code"].astype(str) == student_code].copy()
    return q.sort_values("created_at", ascending=True).to_dict("records")
