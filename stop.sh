#!/bin/bash
echo "🛑 Stopping Paper Search services..."

# Try to stop using PID files first
stopped=0

if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null && stopped=1
    rm backend.pid
    echo "✅ Backend stopped (via PID file)"
fi

if [ -f frontend/frontend.pid ]; then
    kill $(cat frontend/frontend.pid) 2>/dev/null
    rm frontend/frontend.pid
    echo "✅ Frontend stopped (via PID file)"
fi

# If no PID file, find and kill processes by name
if [ $stopped -eq 0 ]; then
    # Kill uvicorn backend
    pkill -f "uvicorn app.main:app" && echo "✅ Backend stopped (via pkill)"
    
    # Kill frontend server
    pkill -f "frontend/server.py" && echo "✅ Frontend stopped (via pkill)"
fi

# Wait a moment for processes to stop
sleep 1

# Check if any processes are still running
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "⚠️  Backend still running, forcing stop..."
    pkill -9 -f "uvicorn app.main:app"
fi

if pgrep -f "frontend/server.py" > /dev/null; then
    echo "⚠️  Frontend still running, forcing stop..."
    pkill -9 -f "frontend/server.py"
fi

echo "✨ All services stopped"
