#!/bin/bash
# Start Voice Bot Service with filtered ONNX GPU warning
source venv/bin/activate
python3 -u main_voice.py 2>&1 | grep --line-buffered -v -E "GPU device discovery failed|device_discovery\.cc|DiscoverDevicesForPlatform"
