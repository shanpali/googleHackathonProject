#!/bin/bash

# MCP Integration Startup Script
# This script helps you test the MCP integration step by step

echo "🚀 MCP Integration Startup Script"
echo "=================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Step 1: Check if Go MCP server is running
echo "Step 1: Checking Go MCP server (port 8080)..."
if check_port 8080; then
    echo "✅ Go MCP server is running on port 8080"
else
    echo "❌ Go MCP server not running. Starting it..."
    echo "Please run in another terminal:"
    echo "  cd ../../../fi-mcp-dev && go run main.go"
    echo ""
    echo "Press Enter when the server is running..."
    read -r
fi

# Step 2: Test MCP client integration
echo -e "\nStep 2: Testing MCP client integration..."
python3 test_integration.py
if [ $? -eq 0 ]; then
    echo "✅ MCP integration tests passed"
else
    echo "❌ MCP integration tests failed"
    exit 1
fi

# Step 3: Check if Flask server is running
echo -e "\nStep 3: Checking Flask server (port 5000)..."
if check_port 5000; then
    echo "✅ Flask server is already running on port 5000"
else
    echo "❌ Flask server not running. Starting it..."
    echo "Starting Flask server in the background..."
    python3 app.py &
    FLASK_PID=$!
    echo "Flask server started with PID: $FLASK_PID"
    
    # Wait for Flask to start
    sleep 3
    
    if check_port 5000; then
        echo "✅ Flask server is now running on port 5000"
    else
        echo "❌ Failed to start Flask server"
        exit 1
    fi
fi

# Step 4: Test the MCP tools endpoint
echo -e "\nStep 4: Testing MCP tools endpoint..."
response=$(curl -s -w "%{http_code}" http://localhost:5000/mcp-tools)
http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" = "200" ]; then
    echo "✅ MCP tools endpoint is working"
    echo "Response preview:"
    echo "$body" | python3 -m json.tool | head -20
    echo "..."
else
    echo "❌ MCP tools endpoint failed (HTTP $http_code)"
    echo "$body"
fi

# Step 5: Test chatbot with MCP tools
echo -e "\nStep 5: Testing chatbot with MCP integration..."
echo "Sending test message to chatbot..."

# First login
login_response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"phone": "1234567890"}' \
    -c cookies.txt \
    http://localhost:5000/login)

echo "Login response: $login_response"

# Then test chatbot
chat_response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"message": "What financial tools do you have available?"}' \
    -b cookies.txt \
    http://localhost:5000/chatbot)

echo "Chat response preview:"
echo "$chat_response" | python3 -m json.tool | head -30

# Cleanup
rm -f cookies.txt

echo -e "\n🎉 MCP Integration Test Complete!"
echo "=================================="
echo "Your MCP integration is now ready to use."
echo ""
echo "Available endpoints:"
echo "  - GET  /mcp-tools     - List available MCP tools"
echo "  - POST /login         - Login with phone number"
echo "  - POST /chatbot       - Chat with Gemini + MCP tools"
echo "  - GET  /financial-data - Get user financial data"
echo ""
echo "Example usage:"
echo "  curl -X POST -H 'Content-Type: application/json' \\"
echo "       -d '{\"phone\": \"1234567890\"}' \\"
echo "       http://localhost:5000/login"
echo ""
echo "  curl -X POST -H 'Content-Type: application/json' \\"
echo "       -d '{\"message\": \"Show me my bank transactions\"}' \\"
echo "       -b cookies.txt \\"
echo "       http://localhost:5000/chatbot"
