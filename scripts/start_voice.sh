#!/bin/bash
cd /home/ubuntu/speak-to-input
source venv/bin/activate
pkill -f main_voice.py || true
sleep 2
nohup python main_voice.py > logs/voice_bot.log 2>&1 &
echo "Voice Bot started. PID: $!"
