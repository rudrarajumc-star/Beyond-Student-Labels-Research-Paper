#!/bin/zsh
cd "$(dirname "$0")"
if pgrep -f "src/run_study.py|src/generate.py" > /dev/null; then
  echo "Already running! Use CHECK PROGRESS instead."
else
  export PYTHONUNBUFFERED=1
  nohup caffeinate -i python3 src/run_study.py > run.log 2>&1 &
  echo "Study launched (PID $!). Live progress below — closing this window will NOT stop the run."
fi
sleep 3
tail -f run.log
