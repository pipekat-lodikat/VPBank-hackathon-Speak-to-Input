#!/bin/bash
pkill -f main_browser_service.py
sleep 2
cd /home/ubuntu/speak-to-input
source venv/bin/activate
nohup python main_browser_service.py > logs/browser_agent.log 2>&1 &
echo "Browser agent restarted. PID: $!"
