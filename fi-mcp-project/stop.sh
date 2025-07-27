#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping Financial Dashboard servers...${NC}"
echo "=================================================="

# Function to kill process by port
kill_by_port() {
    local port=$1
    local process_name=$2
    
    echo -e "${YELLOW}🔍 Looking for $process_name on port $port...${NC}"
    
    # Find PID by port
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pid" ]; then
        echo -e "${GREEN}✅ Found $process_name (PID: $pid) on port $port${NC}"
        kill $pid 2>/dev/null
        sleep 2
        
        # Check if process is still running
        if kill -0 $pid 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Process still running, force killing...${NC}"
            kill -9 $pid 2>/dev/null
        fi
        
        echo -e "${GREEN}✅ Stopped $process_name${NC}"
    else
        echo -e "${BLUE}ℹ️  No $process_name found on port $port${NC}"
    fi
}

# Stop FI-MCP server (port 8484)
kill_by_port 8484 "FI-MCP Server"

# Stop Flask backend (default port 5001)
kill_by_port 5001 "Flask Backend"

# Stop React frontend (port 3000)
kill_by_port 3000 "React Frontend"

# Also check for any remaining Python processes from our app
echo -e "${YELLOW}🔍 Cleaning up any remaining Python processes...${NC}"
pkill -f "python.*app.py" 2>/dev/null

# Also check for any remaining Go processes from FI-MCP
echo -e "${YELLOW}🔍 Cleaning up any remaining Go processes...${NC}"
pkill -f "go.*run" 2>/dev/null

echo ""
echo -e "${GREEN}🎉 All servers stopped successfully!${NC}"
echo "==================================================" 