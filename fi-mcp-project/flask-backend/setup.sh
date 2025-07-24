#!/bin/bash

# Enhanced Gemini AI Integration Setup Script

echo "🚀 Setting up Enhanced Gemini AI Integration..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed. Please install pip first."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies. Please check your Python environment."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one with your Gemini API key:"
    echo "   GEMINI_API_KEY=your_api_key_here"
    echo "   You can copy from .env.example if it exists"
else
    echo "✅ .env file found!"
fi

# Create example environment file if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo "📝 Creating .env.example file..."
    cat > .env.example << 'EOF'
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-pro
GEMINI_FLASH_MODEL=gemini-2.5-flash

# Flask Configuration  
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
FLASK_PORT=5001

# Default AI Instructions
DEFAULT_SYSTEM_INSTRUCTION=You are a professional financial advisor and wealth manager. Provide accurate, helpful, and personalized financial advice based on the user's data and questions. Always prioritize the user's financial well-being and provide actionable insights.
EOF
    echo "✅ Created .env.example file"
fi

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Make sure your .env file contains a valid GEMINI_API_KEY"
echo "2. Run the example: python3 gemini.py"
echo "3. Start the Flask app: python3 app.py"
echo "4. Check the documentation in README_GEMINI.md"
echo ""
echo "📚 Available endpoints:"
echo "   • POST /chatbot - Interactive chat with AI assistant"
echo "   • GET /recommendations - Generate financial recommendations"
echo "   • POST /login - User authentication"
echo "   • GET /financial-data - Get user financial data"
echo ""
