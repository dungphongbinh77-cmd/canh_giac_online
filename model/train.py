from pathlib import Path
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "messages.csv"
MODEL_OUT = ROOT / "model" / "classifier.joblib"


def make_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=1000, random_state=42))
    ])


def report(name, model, frame):
    pred = model.predict(frame["message"])
    print(f"\n===== {name} =====")
    print("Accuracy:", round(accuracy_score(frame["label"], pred), 4))
    print("Confusion matrix:")
    print(confusion_matrix(frame["label"], pred))
    print("Classification report:")
    print(classification_report(frame["label"], pred, digits=4))


df = pd.read_csv(DATA)
required = {"message", "label", "split"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Thiếu cột bắt buộc: {sorted(missing)}")

train_df = df[df["split"] == "train"].copy()
val_df = df[df["split"] == "validation"].copy()
test_df = df[df["split"] == "test"].copy()

print("Số mẫu train:", len(train_df))
print("Số mẫu validation:", len(val_df))
print("Số mẫu test:", len(test_df))

model = make_pipeline()
model.fit(train_df["message"], train_df["label"])
report("VALIDATION", model, val_df)
report("TEST", model, test_df)

# Mô hình cuối dùng trong app: train + validation. Tập test không tham gia huấn luyện.
final_df = pd.concat([train_df, val_df], ignore_index=True)
final_model = make_pipeline()
final_model.fit(final_df["message"], final_df["label"])
joblib.dump(final_model, MODEL_OUT)
print(f"\nĐã lưu mô hình cuối tại: {MODEL_OUT}")
print("Lưu ý: Không dùng kết quả trên dữ liệu mô phỏng này làm kết luận cuối của đề tài KHKT.")
