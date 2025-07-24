#!/bin/bash

# Start the Fi-mcp Go server
#cd "$(dirname "$0")"
#echo "Starting Fi-mcp server on port 8080..."
#FI_MCP_PORT=8080 go run . &
#GO_PID=$!

# Start the Flask backend
cd flask-backend
if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment for Flask backend..."
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
echo "Starting Flask backend on port 5000..."
export FLASK_RUN_PORT=5000
python app.py &
FLASK_PID=$!
deactivate
cd ..

# Start the React frontend
cd react-frontend
if [ ! -d "node_modules" ]; then
  echo "Installing React frontend dependencies..."
  npm install
fi
echo "Starting React frontend on port 3000..."
PORT=3000 npm start &
REACT_PID=$!
cd ..

# Print instructions
cat <<EOM

All servers are starting (in the background):
- Fi-mcp server (Go):      http://localhost:8080
- Flask backend (Python):  http://localhost:5000
- React frontend:          http://localhost:3000

To stop all servers, you may need to run:
  kill $GO_PID $FLASK_PID $REACT_PID

EOM 
