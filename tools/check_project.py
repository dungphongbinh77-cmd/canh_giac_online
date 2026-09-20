from pathlib import Path
import csv
import sys

ROOT = Path(__file__).resolve().parents[1]
required = [
    ROOT / "app.py",
    ROOT / "requirements.txt",
    ROOT / "model" / "classifier.joblib",
    ROOT / "model" / "train.py",
    ROOT / "data" / "messages.csv",
    ROOT / "data" / "situations.csv",
    ROOT / "data" / "pretest.csv",
    ROOT / "data" / "posttest.csv",
    ROOT / "data" / "students.csv",
    ROOT / "modules" / "storage.py",
    ROOT / "modules" / "warning_rules.py",
]

errors = []
for p in required:
    if not p.exists():
        errors.append(f"THIEU: {p.relative_to(ROOT)}")

# Basic CSV validation
for name, cols in {
    "messages.csv": {"message", "label"},
    "situations.csv": {"question", "A", "B", "C", "D", "answer"},
    "pretest.csv": {"question_id", "construct", "question", "A", "B", "C", "D", "answer"},
    "posttest.csv": {"question_id", "construct", "question", "A", "B", "C", "D", "answer"},
    "students.csv": {"student_code", "group"},
}.items():
    p = ROOT / "data" / name
    if not p.exists():
        continue
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])
        missing = cols - headers
        if missing:
            errors.append(f"{name}: thieu cot {sorted(missing)}")

# Secret leak checks
for forbidden in [ROOT / ".streamlit" / "secrets.toml", ROOT / "service_account.json", ROOT / "credentials.json"]:
    if forbidden.exists():
        errors.append(f"BAO MAT: khong upload tep nay len GitHub: {forbidden.relative_to(ROOT)}")

print("=== KIEM TRA DU AN CANH GIAC ONLINE ===")
if errors:
    for e in errors:
        print("[LOI]", e)
    print("\nCHUA SAN SANG DEPLOY")
    sys.exit(1)

print("[OK] Cau truc tep day du")
print("[OK] CSV co cac cot bat buoc")
print("[OK] Khong phat hien tep secret cam trong thu muc du an")
print("\nSAN SANG DEPLOY")
