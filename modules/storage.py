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

RESEARCH_HEADERS = [
    "student_code", "group", "test_type", "question_id", "construct",
    "selected_answer", "correct_answer", "is_correct", "attempt_id", "submitted_at"
]


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def normalize_student_code(raw: str) -> str:
    raw = (raw or "").strip().upper()
    raw = re.sub(r"[^A-Z0-9_-]", "", raw)
    return raw[:24]


def valid_student_code(code: str) -> bool:
    return 3 <= len(code) <= 24


# ---------------- SQLite fallback ----------------

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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS research_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_code TEXT NOT NULL,
                group_name TEXT NOT NULL,
                test_type TEXT NOT NULL,
                question_id TEXT NOT NULL,
                construct TEXT NOT NULL,
                selected_answer TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                attempt_id TEXT NOT NULL,
                submitted_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _sqlite_research_df() -> pd.DataFrame:
    with _connect_sqlite() as conn:
        df = pd.read_sql_query(
            "SELECT student_code, group_name AS 'group', test_type, question_id, construct, selected_answer, correct_answer, is_correct, attempt_id, submitted_at FROM research_responses",
            conn,
        )
    return df


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


# ---------------- Google Sheets backend ----------------

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


def _ensure_worksheet(book, title: str, headers: list[str]):
    try:
        ws = book.worksheet(title)
    except Exception:
        ws = book.add_worksheet(title=title, rows=2000, cols=max(10, len(headers)))
    values = ws.row_values(1)
    if not values:
        ws.append_row(headers, value_input_option="RAW")
    return ws


def _google_book():
    secrets = _get_streamlit_secrets()
    gc = _google_client()
    return gc.open_by_key(str(secrets["spreadsheet_id"]))


def _google_quiz_ws():
    return _ensure_worksheet(_google_book(), "quiz_attempts", QUIZ_HEADERS)


def _google_checks_ws():
    return _ensure_worksheet(_google_book(), "message_checks", CHECK_HEADERS)


def _google_research_ws():
    return _ensure_worksheet(_google_book(), "research_responses", RESEARCH_HEADERS)


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


def _google_research_df() -> pd.DataFrame:
    return _worksheet_df(_google_research_ws(), RESEARCH_HEADERS)


# ---------------- Public API ----------------

def init_db():
    """Initialize local fallback. Google Sheets tabs are created lazily on first write/read."""
    _init_sqlite()


def storage_mode() -> str:
    return "Google Sheets" if _google_configured() else "SQLite cục bộ"


def storage_health() -> tuple[bool, str]:
    if not _google_configured():
        return True, "Đang dùng SQLite cục bộ (chưa cấu hình Google Sheets)."
    try:
        book = _google_book()
        _ensure_worksheet(book, "quiz_attempts", QUIZ_HEADERS)
        _ensure_worksheet(book, "message_checks", CHECK_HEADERS)
        _ensure_worksheet(book, "research_responses", RESEARCH_HEADERS)
        return True, "Kết nối Google Sheets thành công."
    except Exception as exc:
        return False, f"Không kết nối được Google Sheets: {type(exc).__name__}: {exc}"


def save_quiz_attempt(student_code: str, question_id: str, category: str, selected_answer: str, correct_answer: str):
    row = [
        student_code, str(question_id), category, selected_answer,
        correct_answer, int(selected_answer == correct_answer), _now()
    ]
    if _google_configured():
        try:
            _google_quiz_ws().append_row(row, value_input_option="RAW")
            return
        except Exception:
            pass

    with _connect_sqlite() as conn:
        conn.execute(
            "INSERT INTO quiz_attempts (student_code, question_id, category, selected_answer, correct_answer, is_correct, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            tuple(row),
        )
        conn.commit()


def save_message_check(student_code: str, risk_score: float, risk_level: str, warning_signs: list[str]):
    row = [student_code, float(risk_score), risk_level, "; ".join(warning_signs), _now()]
    if _google_configured():
        try:
            _google_checks_ws().append_row(row, value_input_option="RAW")
            return
        except Exception:
            pass

    with _connect_sqlite() as conn:
        conn.execute(
            "INSERT INTO message_checks (student_code, risk_score, risk_level, warning_signs, created_at) VALUES (?, ?, ?, ?, ?)",
            tuple(row),
        )
        conn.commit()


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
    if attempts:
        correct = pd.to_numeric(q["is_correct"], errors="coerce").fillna(0).astype(int).sum()
    else:
        correct = 0
    return {
        "attempts": int(attempts),
        "correct": int(correct),
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


def recent_attempts(student_code: str, limit: int = 20) -> list[dict]:
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


def teacher_summary() -> dict:
    quiz = _quiz_df()
    checks = _checks_df()
    if quiz.empty:
        return {
            "students": 0, "quiz_attempts": 0, "correct": 0,
            "accuracy": 0.0, "message_checks": len(checks),
            "category_stats": [], "student_stats": [],
        }
    quiz = quiz.copy()
    quiz["is_correct"] = pd.to_numeric(quiz["is_correct"], errors="coerce").fillna(0).astype(int)
    students = int(quiz["student_code"].astype(str).nunique())
    attempts = len(quiz)
    correct = int(quiz["is_correct"].sum())

    category_rows = []
    for category, group in quiz.groupby("category", dropna=False):
        n = len(group)
        c = int(group["is_correct"].sum())
        category_rows.append({
            "category": str(category), "attempts": n, "correct": c,
            "accuracy": round(c / n * 100, 1) if n else 0.0,
        })

    student_rows = []
    for code, group in quiz.groupby("student_code"):
        n = len(group)
        c = int(group["is_correct"].sum())
        student_rows.append({
            "student_code": str(code), "attempts": n, "correct": c,
            "accuracy": round(c / n * 100, 1) if n else 0.0,
        })

    return {
        "students": students,
        "quiz_attempts": attempts,
        "correct": correct,
        "accuracy": float(correct / attempts * 100) if attempts else 0.0,
        "message_checks": int(len(checks)),
        "category_stats": sorted(category_rows, key=lambda x: x["category"]),
        "student_stats": sorted(student_rows, key=lambda x: x["student_code"]),
    }


def export_all_quiz_attempts() -> pd.DataFrame:
    return _quiz_df().copy()


def export_all_message_checks() -> pd.DataFrame:
    return _checks_df().copy()


# ---------------- Research pre/post API ----------------

def _research_df() -> pd.DataFrame:
    if _google_configured():
        try:
            return _google_research_df()
        except Exception:
            pass
    return _sqlite_research_df()


def has_completed_test(student_code: str, test_type: str) -> bool:
    df = _research_df()
    if df.empty:
        return False
    m = (df["student_code"].astype(str) == str(student_code)) & (df["test_type"].astype(str) == str(test_type))
    return bool(m.any())


def save_research_test(student_code: str, group_name: str, test_type: str, responses: list[dict]):
    """Save one full pre/post test. responses items need question_id, construct, selected_answer, correct_answer."""
    import uuid
    attempt_id = uuid.uuid4().hex[:12]
    submitted_at = _now()
    rows = []
    for r in responses:
        selected = str(r["selected_answer"])
        correct = str(r["correct_answer"])
        rows.append([
            student_code, group_name, test_type, str(r["question_id"]), str(r["construct"]),
            selected, correct, int(selected == correct), attempt_id, submitted_at
        ])

    if _google_configured():
        try:
            ws = _google_research_ws()
            ws.append_rows(rows, value_input_option="RAW")
            return
        except Exception:
            pass

    with _connect_sqlite() as conn:
        conn.executemany(
            "INSERT INTO research_responses (student_code, group_name, test_type, question_id, construct, selected_answer, correct_answer, is_correct, attempt_id, submitted_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()


def student_research_summary(student_code: str) -> dict:
    df = _research_df()
    out = {"PRE": None, "POST": None}
    if df.empty:
        return out
    q = df[df["student_code"].astype(str) == str(student_code)].copy()
    if q.empty:
        return out
    q["is_correct"] = pd.to_numeric(q["is_correct"], errors="coerce").fillna(0).astype(int)
    for typ in ["PRE", "POST"]:
        g = q[q["test_type"].astype(str) == typ]
        if not g.empty:
            score = int(g["is_correct"].sum())
            total = len(g)
            out[typ] = {"score": score, "total": total, "percent": round(score/total*100,1) if total else 0.0}
    return out


def research_teacher_summary() -> dict:
    df = _research_df()
    if df.empty:
        return {"students":0,"rows":0,"scores":[],"group_summary":[],"construct_summary":[]}
    df = df.copy()
    df["is_correct"] = pd.to_numeric(df["is_correct"], errors="coerce").fillna(0).astype(int)
    score_rows=[]
    for (code, group_name, test_type, attempt_id), g in df.groupby(["student_code","group","test_type","attempt_id"], dropna=False):
        total=len(g); score=int(g["is_correct"].sum())
        score_rows.append({"student_code":str(code),"group":str(group_name),"test_type":str(test_type),"score":score,"total":total,"percent":round(score/total*100,1) if total else 0.0})
    scores=pd.DataFrame(score_rows)
    group_rows=[]
    if not scores.empty:
        for (grp, typ), g in scores.groupby(["group","test_type"]):
            group_rows.append({"group":grp,"test_type":typ,"n":int(len(g)),"mean_score":round(float(g["score"].mean()),2),"mean_percent":round(float(g["percent"].mean()),1)})
    construct_rows=[]
    for (grp, typ, construct), g in df.groupby(["group","test_type","construct"]):
        n=len(g); c=int(g["is_correct"].sum())
        construct_rows.append({"group":str(grp),"test_type":str(typ),"construct":str(construct),"items":n,"correct":c,"accuracy":round(c/n*100,1) if n else 0.0})
    return {"students":int(df["student_code"].astype(str).nunique()),"rows":int(len(df)),"scores":score_rows,"group_summary":group_rows,"construct_summary":construct_rows}


def export_research_responses() -> pd.DataFrame:
    return _research_df().copy()
