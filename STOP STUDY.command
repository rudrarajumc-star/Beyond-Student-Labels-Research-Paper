#!/bin/zsh
pkill -f "src/run_study.py" 2>/dev/null
pkill -f "src/generate.py" 2>/dev/null
sleep 1
pgrep -f "src/run_study.py|src/generate.py" > /dev/null && echo "still stopping..." || echo "Stopped. Double-click START STUDY to resume anytime."
