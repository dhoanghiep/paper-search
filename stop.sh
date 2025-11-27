#!/bin/bash
echo "🛑 Stopping Paper Search services..."

if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
    echo "✅ Backend stopped"
fi

if [ -f frontend/frontend.pid ]; then
    kill $(cat frontend/frontend.pid) 2>/dev/null
    rm frontend/frontend.pid
    echo "✅ Frontend stopped"
fi

echo "✨ All services stopped"
