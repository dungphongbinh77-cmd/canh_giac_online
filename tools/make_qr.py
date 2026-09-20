import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--output', default='QR_CANH_GIAC_ONLINE.png')
args = parser.parse_args()

try:
    import qrcode
except ImportError:
    raise SystemExit('Can cai: python -m pip install "qrcode[pil]"')

root = Path(__file__).resolve().parents[1]
out = root / args.output
img = qrcode.make(args.url)
img.save(out)
print(f'Da tao QR: {out}')
