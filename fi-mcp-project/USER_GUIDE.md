# User Guide: ArthaSetu AI Mock Financial Dashboard

This guide explains how to set up, configure, and use the ArthaSetu AI mock financial dashboard project, which provides a full-stack mock financial dashboard with recommendations.

---

## How This Solves the Google Hackathon Challenge

- **Structured Financial Data**: The backend serves user-specific, structured financial data (assets, liabilities, net worth, credit, EPF, and more) in JSON format, just like Fi MCP.
- **AI-Powered Insights**: Integrates with Gemini (Google AI) to provide personalized, context-aware financial advice and recommendations.
- **Natural Language Conversations**: Users can chat with the AI agent about their finances, simulate scenarios, and get actionable insights.
- **User Privacy and Control**: All data is session-based, never leaves the server except for AI processing, and users can export their insights.
- **Extensible, Modern UI**: The React dashboard visualizes net worth, asset allocation, recent transactions, and more, and can be extended for scenario simulation and anomaly detection.
- **Google AI Technologies**: Uses Gemini for all AI-powered insights and recommendations.

---

## About the Data (Demo Mode)

**Note:**
For this hackathon/demo, the backend serves **mock financial data** from `test_data_dir/` instead of connecting to the real Fi MCP server. Each directory in `test_data_dir` represents a different user scenario, allowing us to simulate a wide range of financial profiles and test the AI agent’s capabilities. The architecture is ready to connect to the real Fi MCP server with minimal changes.

---

## New Features

- **Export Insights**: Download your personalized financial insights as a JSON file with one click.
- **Scenario Simulation**: Ask the chatbot "What if" questions (e.g., "What if I increase my SIP by ₹5,000?") and get AI-powered projections and advice.

---

## Overview

This project consists of two main components:

1. **Flask Backend** (serves all mock data and APIs, Python)
2. **React Frontend** (user dashboard, JavaScript)

All components are orchestrated via simple startup scripts for easy startup.

---

## Directory Structure

```
fi-mcp-project/
├── flask-backend/         # Flask backend (Python)
│   ├── app.py
│   └── requirements.txt
├── react-frontend/        # React frontend (JavaScript)
│   ├── package.json
│   └── src/
├── test_data_dir/         # Dummy data for Flask backend
└── ...                    # Other files
```

---

## Prerequisites

- **Python 3** (for Flask backend)
- **Node.js & npm** (for React frontend)

---

## Setup & Running the Project

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repo-url>
   cd fi-mcp-project
   ```

2. **Install and start Flask backend**
   ```bash
   cd flask-backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```

3. **Start React frontend**
   ```bash
   cd ../react-frontend
   npm install
   npm start
   ```

4. **Access the Dashboard**
   - Open [http://localhost:3000](http://localhost:3000) in your browser.
   - Log in with any allowed phone number (see `test_data_dir/` for options).

---

## Technologies Used

| Component         | Technology   | Purpose                                              |
|-------------------|-------------|------------------------------------------------------|
| Flask Backend     | Python/Flask| Serves all mock data and APIs                        |
| React Frontend    | React/JS    | User dashboard, charts, and recommendations UI        |

---

## Customization

- **Add More Dummy Data:**
  - Place new JSON files in each user's directory under `test_data_dir/`.
  - Update `DATA_ENDPOINTS` in `flask-backend/app.py` to include new endpoints.
  - Add new sections to the React dashboard as needed.

- **Change Ports:**
  - Edit the startup scripts and the relevant server files if you need to use different ports.

---

## Troubleshooting

- If a server fails to start, check for missing dependencies and install them as prompted.
- If you see CORS errors, ensure all servers are running and ports are correct.
- To stop all servers, use your terminal to kill the running processes.

---

## FAQ

**Q: What phone numbers can I use to log in?**
A: Any directory name in `test_data_dir/` is a valid phone number for login.

**Q: Is this safe for demos?**
A: Yes, all data is static and there are no real integrations.

---

For further help, check the README or contact the project maintainer. 