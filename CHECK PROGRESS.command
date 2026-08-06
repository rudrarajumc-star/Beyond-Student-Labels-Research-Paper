#!/bin/zsh
cd "$(dirname "$0")"
echo "=== Is it running? ==="
pgrep -f "src/run_study.py|src/generate.py" > /dev/null && echo "YES - running" || echo "NO - not running (double-click START STUDY to launch/resume)"
echo
echo "=== Results so far ==="
python3 -c "
import json, collections
try:
    c = collections.Counter((r['model_family'], str(r['parse_status'])[:25]) for r in map(json.loads, open('data/generations.jsonl')))
    total = sum(c.values())
    print(f'{total} / 2160 generations collected')
    [print(f'  {k[0]:>8} | {k[1]:<25} | {v}') for k, v in sorted(c.items())]
except FileNotFoundError:
    print('no data yet')"
echo
echo "=== Last 10 log lines ==="
tail -10 run.log 2>/dev/null || echo "(no log yet)"
