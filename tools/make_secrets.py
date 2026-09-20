import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--json', required=True, help='Duong dan file Service Account JSON')
parser.add_argument('--spreadsheet-id', required=True)
parser.add_argument('--output', default='.streamlit/secrets.toml')
args = parser.parse_args()

info = json.loads(Path(args.json).read_text(encoding='utf-8'))
root = Path(__file__).resolve().parents[1]
out = root / args.output
out.parent.mkdir(parents=True, exist_ok=True)
private_key = info['private_key'].replace('"""', '')
text = f'''spreadsheet_id = "{args.spreadsheet_id}"

[gcp_service_account]
type = "{info.get('type','service_account')}"
project_id = "{info['project_id']}"
private_key_id = "{info['private_key_id']}"
private_key = """{private_key}"""
client_email = "{info['client_email']}"
client_id = "{info['client_id']}"
auth_uri = "{info.get('auth_uri','https://accounts.google.com/o/oauth2/auth')}"
token_uri = "{info.get('token_uri','https://oauth2.googleapis.com/token')}"
auth_provider_x509_cert_url = "{info.get('auth_provider_x509_cert_url','https://www.googleapis.com/oauth2/v1/certs')}"
client_x509_cert_url = "{info.get('client_x509_cert_url','')}"
universe_domain = "{info.get('universe_domain','googleapis.com')}"
'''
out.write_text(text, encoding='utf-8')
print(f'Da tao: {out}')
print('KHONG upload file secrets.toml len GitHub.')
