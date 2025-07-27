# FI-MCP Financial Advisor Project

## 📋 Project Overview

FI-MCP is an advanced AI-powered financial advisory platform built for the hackathon. It provides comprehensive financial analysis, personalized recommendations, and intelligent insights using a custom financial agent with ADK (Agent Development Kit) compliance.

### 🎯 Key Features

- **AI-Powered Financial Analysis**: Custom financial agent with Indian financial context
- **Real-time Data Integration**: FI-MCP server integration for live financial data
- **Comprehensive Dashboard**: Portfolio analysis, health scores, insights, and recommendations
- **Goal Planning**: AI-driven goal suggestions and tracking
- **Lending Analysis**: "Udhaar Aur Bharosa" - intelligent lending with trust ratings
- **Voice Integration**: Google Voice API for voice-to-text lending entries
- **Tax Optimization**: Indian tax context (80C, 80D, 80TTA) with AI recommendations
- **Proactive Insights**: Salary pattern detection, expense analysis, and alerts

## 🏗️ Project Structure

```
fi-mcp-project/
├── flask-backend/                 # Python Flask backend
│   ├── app.py                    # Main Flask application
│   ├── custom_financial_agent.py # AI financial agent
│   ├── firebase_config.py        # Firebase configuration
│   ├── firebase_models.py        # Firebase data models
│   ├── requirements.txt          # Python dependencies
│   └── venv/                    # Virtual environment
├── react-frontend/               # React frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Dashboard.js     # Main dashboard
│   │   │   ├── Portfolio.js     # Portfolio analysis
│   │   │   ├── Goals.js         # Goal planning
│   │   │   ├── Insights.js      # Financial insights
│   │   │   ├── HealthScore.js   # Health score
│   │   │   └── UdhaarAurBharosa.js # Lending feature
│   │   ├── App.js              # Main app component
│   │   └── index.js            # App entry point
│   ├── package.json            # Node.js dependencies
│   └── public/                 # Static files
├── test_data_dir/              # Mock financial data
├── static/                     # Static assets
├── middlewares/                # Go middleware
├── pkg/                        # Go packages
├── run.sh                      # Startup script
├── stop.sh                     # Shutdown script
└── README.md                   # This file
```

## 🚀 Technology Stack

### Backend
- **Python Flask**: Web framework
- **Custom Financial Agent**: AI-powered analysis with ADK compliance
- **Firebase**: Database and authentication
- **Google Gemini AI**: Natural language processing
- **Google Cloud APIs**: Speech-to-text, Natural Language

### Frontend
- **React.js**: Frontend framework
- **Material-UI (MUI)**: UI components
- **Axios**: HTTP client
- **Chart.js**: Data visualization

### External Services
- **FI-MCP Server**: Real financial data (Go server on port 8484)
- **Firebase Firestore**: Database
- **Google Cloud**: AI and voice services

## 📦 Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Firebase project setup
- Google Cloud project with APIs enabled

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fi-mcp-project
```

### 2. Backend Setup

```bash
cd flask-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_gemini_api_key"
export FIREBASE_PROJECT_ID="your_firebase_project_id"
export FIREBASE_PRIVATE_KEY="your_firebase_private_key"
export FIREBASE_CLIENT_EMAIL="your_firebase_client_email"
```

### 3. Frontend Setup

```bash
cd react-frontend

# Install dependencies
npm install

# Set environment variables (create .env file)
echo "REACT_APP_API_URL=http://localhost:5001" > .env
```

### 4. Firebase Configuration

1. Create a Firebase project
2. Enable Firestore database
3. Create service account and download credentials
4. Update `firebase_config.py` with your credentials

### 5. Google Cloud Setup

1. Create Google Cloud project
2. Enable APIs:
   - Gemini AI API
   - Speech-to-Text API
   - Natural Language API
3. Create API key and set `GEMINI_API_KEY`

## 🏃‍♂️ Running the Project

### 1. Start Backend Server

```bash
cd flask-backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

Backend will run on `http://localhost:5001`

### 2. Start Frontend Development Server

```bash
cd react-frontend
npm start
```

Frontend will run on `http://localhost:3000`

### 3. Start FI-MCP Server (Optional)

```bash
# If you have the fi-mcp server
./fi-mcp-server  # or your specific command
```

FI-MCP server should run on `http://localhost:8484`

### 4. Using the Startup Script

```bash
# Start all services
./run.sh

# Stop all services
./stop.sh
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the flask-backend directory:

```env
GEMINI_API_KEY=your_gemini_api_key
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY=your_firebase_private_key
FIREBASE_CLIENT_EMAIL=your_firebase_client_email
GOOGLE_CLOUD_PROJECT=your_google_cloud_project
```

### Test Data

The project includes mock financial data in `test_data_dir/` for testing:

- Bank transactions
- Credit reports
- Net worth data
- Mutual fund transactions
- Stock transactions

## 📊 API Endpoints

### Authentication
- `POST /login` - User login with phone number
- `POST /logout` - User logout

### Financial Data
- `GET /financial-data` - Get comprehensive financial data
- `GET /cash-transactions` - Get cash asset transactions
- `POST /cash-asset` - Add/update cash assets

### AI Analysis
- `POST /chatbot` - AI-powered financial chat
- `GET /insights` - Generate financial insights
- `GET /recommendations` - Get personalized recommendations
- `GET /health-score` - Calculate financial health score

### Goal Management
- `GET /goals` - Get user goals
- `POST /goals` - Create/update goals
- `POST /goal-suggestions` - AI-generated goal suggestions

### Lending Feature
- `POST /udhaar/voice-analyze` - Analyze voice for lending
- `POST /udhaar/lend` - Record lending transaction
- `GET /udhaar/lendings` - Get lending history
- `POST /udhaar/lending-analysis` - AI lending analysis

### FI-MCP Integration
- `POST /fi-mcp-auth` - Authenticate with FI-MCP server
- `POST /fi-mcp-retry` - Retry data fetch after authentication
- `GET /test-fi-mcp` - Test FI-MCP connectivity

## 🎯 Key Features Explained

### 1. Custom Financial Agent
- ADK-compliant AI agent
- Indian financial context
- Real-time analysis and recommendations
- Multi-intent detection

### 2. FI-MCP Integration
- Real financial data from external server
- Authentication flow with session management
- Graceful fallback to mock data
- JSON-RPC 2.0 protocol support

### 3. Voice-Enabled Lending
- Google Voice API integration
- Speech-to-text conversion
- Intelligent entity extraction
- Trust rating system

### 4. Proactive Insights
- Salary pattern detection
- Expense analysis
- EMI and auto-debit tracking
- Cash flow analysis

### 5. Goal Planning
- AI-powered goal suggestions
- Conversational goal creation
- Progress tracking
- Financial impact analysis

## 🧪 Testing

### Test Phone Numbers
Use these test phone numbers for different scenarios:
- `9611133087` - Complete financial profile
- `1010101010` - Basic profile
- `9999999999` - Empty profile

### Manual Testing
1. Login with test phone number
2. Navigate through different sections
3. Test voice recording in lending feature
4. Verify FI-MCP authentication flow
5. Check AI responses in chatbot

## 🐛 Troubleshooting

### Common Issues

1. **Backend not starting**
   - Check virtual environment activation
   - Verify environment variables
   - Check port 5001 availability

2. **Frontend not connecting to backend**
   - Verify backend is running on port 5001
   - Check CORS configuration
   - Verify API URL in frontend

3. **FI-MCP server issues**
   - Ensure fi-mcp server is running on port 8484
   - Check authentication flow
   - Verify session management

4. **Voice recording not working**
   - Check browser permissions
   - Verify Google Cloud APIs
   - Check network connectivity

### Debug Mode

Enable debug logging:
```python
# In app.py
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance

- **Backend**: Flask with async support
- **Frontend**: React with optimized rendering
- **Database**: Firebase Firestore with caching
- **AI**: Gemini API with request optimization
- **Caching**: Redis-like caching for insights and health scores

## 🔒 Security

- Firebase authentication
- Session management
- API key protection
- CORS configuration
- Input validation and sanitization

## 📝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is developed for hackathon purposes.

## 🤝 Support

For issues and questions:
1. Check troubleshooting section
2. Review API documentation
3. Check Firebase console
4. Verify Google Cloud setup

---

**Note**: This project is designed for educational and hackathon purposes. For production use, additional security measures and testing should be implemented. 