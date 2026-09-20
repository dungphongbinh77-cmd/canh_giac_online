from __future__ import annotations

import argparse
import json
from pathlib import Path


def toml_string(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Tao .streamlit/secrets.toml tu Service Account JSON")
    parser.add_argument("--json", required=True, help="Duong dan file Service Account JSON")
    parser.add_argument("--spreadsheet-id", required=True, help="Google Spreadsheet ID")
    parser.add_argument("--admin-pin", required=True, help="PIN giao vien")
    parser.add_argument("--public-app-url", default="", help="URL app sau deploy (co the bo trong)")
    args = parser.parse_args()

    json_path = Path(args.json).expanduser().resolve()
    data = json.loads(json_path.read_text(encoding="utf-8"))

    required = [
        "type", "project_id", "private_key_id", "private_key", "client_email", "client_id",
        "auth_uri", "token_uri", "auth_provider_x509_cert_url", "client_x509_cert_url"
    ]
    missing = [k for k in required if not data.get(k)]
    if missing:
        raise SystemExit(f"File JSON thieu truong: {', '.join(missing)}")

    lines = [
        f"spreadsheet_id = {toml_string(args.spreadsheet_id)}",
        f"admin_pin = {toml_string(args.admin_pin)}",
    ]
    if args.public_app_url:
        lines.append(f"public_app_url = {toml_string(args.public_app_url)}")

    lines += ["", "[gcp_service_account]"]
    for key in required:
        lines.append(f"{key} = {toml_string(data[key])}")
    if data.get("universe_domain"):
        lines.append(f"universe_domain = {toml_string(data['universe_domain'])}")

    out = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Da tao: {out}")
    print("KHONG commit tep nay len GitHub.")
    print("Copy noi dung tep vao Streamlit Community Cloud > App settings > Secrets.")


if __name__ == "__main__":
    main()
