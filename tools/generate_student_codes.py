import argparse
import csv
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--count', type=int, default=100)
parser.add_argument('--prefix', default='HS')
parser.add_argument('--class-name', default='')
parser.add_argument('--output', default='data/student_codes.csv')
args = parser.parse_args()

root = Path(__file__).resolve().parents[1]
out = root / args.output
out.parent.mkdir(parents=True, exist_ok=True)
width = max(3, len(str(args.count)))
with out.open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['student_code','class_name','active'])
    for i in range(1, args.count + 1):
        w.writerow([f'{args.prefix}{i:0{width}d}', args.class_name, 1])
print(f'Da tao {args.count} ma tai: {out}')
