#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Financial Dashboard - Flask + React${NC}"
echo "=================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please create a .env file with your configuration:"
    echo "GEMINI_API_KEY=<your-api-key>"
    echo "FLASK_SECRET_KEY=your_secret_key_here"
    echo "FLASK_DEBUG=True"
    echo "FLASK_PORT=5001"
    exit 1
fi

# Note: Do NOT source .env here. Flask will load it using python-dotenv.

# Start the Flask backend
echo -e "${YELLOW}📡 Starting Flask backend...${NC}"
cd "$(dirname "$0")/flask-backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}🔧 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo -e "${YELLOW}📦 Installing/updating Python dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Start Flask backend
FLASK_PORT_FROM_ENV=$(grep '^FLASK_PORT=' ../.env | cut -d '=' -f2 | tr -d '\r')
FLASK_PORT_TO_USE=${FLASK_PORT_FROM_ENV:-5001}
echo -e "${GREEN}🚀 Starting Flask backend on port ${FLASK_PORT_TO_USE}...${NC}"
python3 app.py &
FLASK_PID=$!
deactivate
cd ..

# Wait a moment for Flask to start
sleep 3

# Check if Flask is running
if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo -e "${RED}❌ Flask backend failed to start!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Flask backend is running (PID: $FLASK_PID)${NC}"

# Start the React frontend
echo -e "${YELLOW}⚛️  Starting React frontend...${NC}"
cd react-frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing React dependencies...${NC}"
    npm install
fi

# Start React frontend
echo -e "${GREEN}🚀 Starting React frontend on port 3000...${NC}"
PORT=3000 npm start &
REACT_PID=$!
cd ..

# Wait a moment for React to start
sleep 5

# Check if React is running
if ! kill -0 $REACT_PID 2>/dev/null; then
    echo -e "${RED}❌ React frontend failed to start!${NC}"
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ React frontend is running (PID: $REACT_PID)${NC}"

# Print success message
echo ""
echo -e "${GREEN}🎉 All servers are running successfully!${NC}"
echo "=================================================="
echo -e "${BLUE}📊 Flask Backend:${NC}  http://localhost:${FLASK_PORT_TO_USE}"
echo -e "${BLUE}🌐 React Frontend:${NC} http://localhost:3000"
echo ""
echo -e "${YELLOW}📝 To stop all servers, run:${NC}"
echo "  kill $FLASK_PID $REACT_PID"
echo ""
echo -e "${YELLOW}📝 Or use the stop script:${NC}"
echo "  ./stop.sh"
echo ""
echo -e "${GREEN}✨ Happy coding!${NC}" 