#!/bin/bash

# Start the Flask backend
cd "$(dirname "$0")/flask-backend"
echo "[run.sh] Starting Flask backend on port 5000..."
if [ ! -d "venv" ]; then
  echo "[run.sh] Creating Python virtual environment for Flask backend..."
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
echo "[run.sh] Running Flask backend..."
python app.py &
FLASK_PID=$!
deactivate
cd ..

# Start the React frontend
cd react-frontend
if [ ! -d "node_modules" ]; then
  echo "[run.sh] Installing React frontend dependencies..."
  npm install
fi
echo "[run.sh] Starting React frontend on port 3000..."
PORT=3000 npm start &
REACT_PID=$!
cd ..

# Print instructions
cat <<EOM

All servers are starting (in the background):
- Flask backend (Python):  http://localhost:5000
- React frontend:          http://localhost:3000

To stop all servers, you may need to run:
  kill $FLASK_PID $REACT_PID

EOM 
