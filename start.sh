#!/bin/bash
echo "🚀 Starting Paper Search Full Stack..."

# Start backend
cd /workshop/paper-search
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
echo "✅ Backend started (PID: $BACKEND_PID) - http://localhost:8000"

# Start frontend
cd frontend
nohup python3 server.py > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid
echo "✅ Frontend started (PID: $FRONTEND_PID) - http://localhost:5173"

echo ""
echo "📊 Services:"
echo "  - Frontend: http://localhost:5173"
echo "  - Backend:  http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop: ./stop.sh"
