#!/bin/zsh
cd "$(dirname "$0")"
export PYTHONUNBUFFERED=1
if pgrep -f "src/judge.py" > /dev/null; then
  echo "Judging already running!"
else
  set -a; source .env; set +a
  nohup python3 src/judge.py > judge.log 2>&1 &
  echo "Judging launched (PID $!). Closing this window will NOT stop it."
fi
sleep 3
tail -f judge.log
