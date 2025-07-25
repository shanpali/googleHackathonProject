# 🚀 Startup Guide - Financial Dashboard

This guide will help you start both the Flask backend and React frontend servers for the Financial Dashboard application.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.8+** - For Flask backend
- **Node.js 16+** - For React frontend
- **npm** - Comes with Node.js
- **Git** - For version control

### Check your installations:
```bash
python3 --version
node --version
npm --version
```

## 🔧 Initial Setup

### 1. Create Environment File
Create a `.env` file in the `fi-mcp-project` directory with the following content:

```env
# Gemini AI Configuration
GEMINI_API_KEY=<your-api-key>
GEMINI_MODEL=gemini-2.5-pro
GEMINI_FLASH_MODEL=gemini-2.5-flash

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
FLASK_PORT=5001

# Default AI Instructions
DEFAULT_SYSTEM_INSTRUCTION=You are a professional financial advisor and wealth manager. Provide accurate, helpful, and personalized financial advice based on the user's data and questions. Always prioritize the user's financial well-being and provide actionable insights.
```

**Important:** Replace `<your-api-key>` with your actual Gemini API key from Google AI Studio.

### 2. Get Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and paste it in your `.env` file

## 🚀 Quick Start (Recommended)

### Option 1: Using the Automated Script
```bash
# Navigate to the project directory
cd fi-mcp-project

# Make scripts executable (if not already done)
chmod +x run.sh stop.sh

# Start both servers
./run.sh
```

### Option 2: Manual Startup

#### Start Flask Backend:
```bash
cd fi-mcp-project/flask-backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Start Flask server
python app.py
```

#### Start React Frontend (in a new terminal):
```bash
cd fi-mcp-project/react-frontend

# Install dependencies (first time only)
npm install

# Start React development server
npm start
```

## 🌐 Accessing the Application

Once both servers are running:

- **React Frontend**: http://localhost:3000
- **Flask Backend API**: http://localhost:5001

## 🛑 Stopping the Servers

### Option 1: Using the Stop Script
```bash
./stop.sh
```

### Option 2: Manual Stop
- Press `Ctrl+C` in each terminal window
- Or find and kill the processes:
  ```bash
  # Find processes on specific ports
  lsof -ti:3000  # React frontend
  lsof -ti:5001  # Flask backend
  
  # Kill them
  kill <PID>
  ```

## 🔍 Troubleshooting

### Common Issues:

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :3000  # For React
lsof -i :5001  # For Flask

# Kill the process
kill -9 <PID>
```

#### 2. Python Virtual Environment Issues
```bash
# Remove and recreate virtual environment
cd flask-backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Node Modules Issues
```bash
# Clear npm cache and reinstall
cd react-frontend
rm -rf node_modules package-lock.json
npm install
```

#### 4. Environment Variables Not Loading
- Ensure `.env` file is in the correct location (`fi-mcp-project/.env`)
- Check that the file has no extra spaces or quotes
- Restart the Flask server after making changes

### Error Messages:

#### "Module not found" (Python)
```bash
cd flask-backend
source venv/bin/activate
pip install -r requirements.txt
```

#### "Module not found" (Node.js)
```bash
cd react-frontend
npm install
```

#### "Permission denied" (Scripts)
```bash
chmod +x run.sh stop.sh
```

## 📊 Verification

To verify everything is working:

1. **Frontend**: Open http://localhost:3000 - should show the login page
2. **Backend**: Open http://localhost:5001 - should show Flask welcome page
3. **API Test**: Try logging in with any phone number from the test data

## 🔄 Development Workflow

1. **Start servers**: `./run.sh`
2. **Make changes** to your code
3. **React** will auto-reload on file changes
4. **Flask** will auto-reload if `FLASK_DEBUG=True`
5. **Stop servers**: `./stop.sh`

## 📝 Logs

- **Flask logs**: Check the terminal where Flask is running
- **React logs**: Check the terminal where React is running
- **Browser logs**: Open Developer Tools (F12) in your browser

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure your `.env` file is properly configured
4. Check the logs for specific error messages
5. Restart both servers completely

---

**Happy coding! 🎉** 