# ArthaSetu AI Mock Financial Dashboard

A minimal, hackathon-ready version of a financial dashboard server. This project provides a lightweight mock server for use in hackathons, demos, and development, simulating the core features of a production financial platform with dummy data and simplified authentication.

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

## Purpose

- **ArthaSetu AI** is designed for hackathon participants and developers who want to experiment with a financial API without accessing real user data or production systems.
- It serves dummy financial data and uses a dummy authentication flow, making it safe and easy to use in non-production environments.

## Features

- **Simulates Financial API**: Implements endpoints for net worth, credit report, EPF details, mutual fund transactions, and bank transactions.
- **Dummy Data**: All responses are served from static JSON files in `test_data_dir/`, representing various user scenarios.
- **Dummy Authentication**: Simple login flow using allowed phone numbers (directory names in `test_data_dir/`). No real OTP or user verification.
- **Gemini API Integration**: Flask backend can provide AI-powered financial advice using Gemini API.
- **Hackathon-Ready**: No real integrations, no sensitive data, and easy to reset or extend.

## Architecture

| Component         | Technology   | Purpose                                              |
|-------------------|-------------|------------------------------------------------------|
| Flask Backend     | Python/Flask| Serves all mock data and Gemini APIs advice           |
| React Frontend    | React/JS    | User dashboard, charts, and recommendations UI        |

## Directory Structure

- `flask-backend/app.py` — Entrypoint, sets up the server and endpoints. Serves all mock data and Gemini API advice.
- `test_data_dir/` — Contains directories named after allowed phone numbers. Each directory holds JSON files for different API responses (e.g., `fetch_net_worth.json`).
- `react-frontend/` — Modern React dashboard UI.

## Dummy Data Scenarios

The dummy data covers a variety of user states. Example scenarios:

- **All assets connected**: Banks, EPF, Indian stocks, US stocks, credit report, large or small mutual fund portfolios.
- **All assets except bank account**: No bank account, but other assets present.
- **Multiple banks and UANs**: Multiple bank accounts and EPF UANs, partial transaction coverage.
- **No assets connected**: Only a savings account balance is present.
- **No credit report**: All assets except credit report.

## Test Data Scenarios

| Phone Number | Description |
|-------------|-------------|
| 1111111111  | No assets connected. Only saving account balance present |
| 2222222222  | All assets connected (Banks account, EPF, Indian stocks, US stocks, Credit report). Large mutual fund portfolio with 9 funds |
| ...         | ... (see test_data_dir for full list) |

## Example: Dummy Data File

A sample `fetch_net_worth.json` (truncated for brevity):

```json
{
  "netWorthResponse": {
    "assetValues": [
      {"netWorthAttribute": "ASSET_TYPE_MUTUAL_FUND", "value": {"currencyCode": "INR", "units": "84642"}},
      {"netWorthAttribute": "ASSET_TYPE_EPF", "value": {"currencyCode": "INR", "units": "211111"}}
    ],
    "liabilityValues": [
      {"netWorthAttribute": "LIABILITY_TYPE_VEHICLE_LOAN", "value": {"currencyCode": "INR", "units": "5000"}}
    ],
    "totalNetWorthValue": {"currencyCode": "INR", "units": "658305"}
  }
}
```

## Authentication Flow

- When a tool/API is called, the server checks for a valid session.
- If not authenticated, the user is prompted to log in via a web page.
- Enter any allowed phone number (see directories in `test_data_dir/`). OTP is not validated.
- On successful login, the session is stored in memory for the duration of the server run.

## Running the Server

### Prerequisites
- Python 3 (for Flask backend)
- Node.js & npm (for React frontend)

### Install dependencies and start Flask backend
```sh
cd flask-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Start the React frontend
```sh
cd ../react-frontend
npm install
npm start
```

The server will start on [http://localhost:5001](http://localhost:5001) and the frontend on [http://localhost:3000](http://localhost:3000).

## Usage
- Log in with any allowed phone number (see `test_data_dir/` for options)
- Otp/Passcode can be anything on the webpage
- View your mock financial dashboard and try different scenarios by logging in with different phone numbers
- Use the chatbot for natural language financial queries and scenario simulation
- Use the Export Insights button to download your personalized insights

## FAQ

**Q: Where do I put my Gemini API key?**
A: In `flask-backend/app.py`, replace `YOUR_GEMINI_API_KEY` in the `GEMINI_API_URL` variable.

**Q: What phone numbers can I use to log in?**
A: Any directory name in `test_data_dir/` is a valid phone number for login.

**Q: Is this safe for demos?**
A: Yes, all data is static and there are no real integrations.

---

For more details, see the USER_GUIDE.md. 