#!/bin/bash
# Bash script to start all microservices manually
# Linux/Mac script

echo "🚀 Starting VPBank Microservices..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found! Please create .env file first."
    exit 1
fi

# Set environment variables
export TASK_QUEUE_SERVICE_URL="http://localhost:7862"

echo ""
echo "📋 Services will start in separate terminal windows"
echo "   1. Task Queue Service (port 7862)"
echo "   2. Voice Bot Service (port 7860)"
echo "   3. Browser Worker Service (background)"
echo ""

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    TERM_CMD="gnome-terminal --"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    TERM_CMD="osascript -e 'tell app \"Terminal\" to do script'"
else
    echo "❌ Unsupported OS. Please start services manually."
    exit 1
fi

# Start Task Queue Service
echo "🌐 Starting Task Queue Service..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    gnome-terminal -- bash -c "cd $PWD && source venv/bin/activate && python services/task_queue_service/main.py; exec bash" &
elif [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell app \"Terminal\" to do script \"cd $PWD && source venv/bin/activate && python services/task_queue_service/main.py\"" &
fi
sleep 3

# Start Voice Bot Service
echo "🎤 Starting Voice Bot Service..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    gnome-terminal -- bash -c "cd $PWD && source venv/bin/activate && export TASK_QUEUE_SERVICE_URL=http://localhost:7862 && python main_voice.py; exec bash" &
elif [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell app \"Terminal\" to do script \"cd $PWD && source venv/bin/activate && export TASK_QUEUE_SERVICE_URL=http://localhost:7862 && python main_voice.py\"" &
fi
sleep 2

# Start Browser Worker Service
echo "🔨 Starting Browser Worker Service..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    gnome-terminal -- bash -c "cd $PWD && source venv/bin/activate && export TASK_QUEUE_SERVICE_URL=http://localhost:7862 && python main_worker.py; exec bash" &
elif [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell app \"Terminal\" to do script \"cd $PWD && source venv/bin/activate && export TASK_QUEUE_SERVICE_URL=http://localhost:7862 && python main_worker.py\"" &
fi

echo ""
echo "✅ All services started!"
echo "📝 Check the terminal windows for logs"
echo ""
echo "🌐 Access points:"
echo "   - Voice Bot: http://localhost:7860"
echo "   - Task Queue API: http://localhost:7862/api/health"
echo ""

