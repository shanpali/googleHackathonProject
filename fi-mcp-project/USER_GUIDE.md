# User Guide: Fi-mcp Demo Project

This guide explains how to set up, configure, and use the Fi-mcp demo project, which provides a full-stack mock financial dashboard with recommendations.

---

## Overview

This project consists of three main components:

1. **Fi-mcp Go Server** (mock backend, Go)
2. **Flask Backend** (API aggregator and Gemini integration, Python)
3. **React Frontend** (user dashboard, JavaScript)

All components are orchestrated via a single `run.sh` script for easy startup.

---

## Directory Structure

```
fi-mcp-dev-master/
├── flask-backend/         # Flask backend (Python)
│   ├── app.py
│   └── requirements.txt
├── react-frontend/        # React frontend (JavaScript)
│   ├── package.json
│   └── src/
├── test_data_dir/         # Dummy data for Fi-mcp Go server
├── run.sh                 # Startup script
└── ...                    # Go server files (main.go, etc.)
```

---

## Prerequisites

- **Go** (v1.23 or later)
- **Python 3** (for Flask backend)
- **Node.js & npm** (for React frontend)

---

## Setup & Running the Project

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repo-url>
   cd fi-mcp-dev-master
   ```

2. **Replace Gemini API Key**
   - Open `flask-backend/app.py`
   - Find the line:
     ```python
     GEMINI_API_URL = 'https://gemini.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_GEMINI_API_KEY'
     ```
   - Replace `YOUR_GEMINI_API_KEY` with your actual Gemini API key.

3. **Start all servers**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   This will:
   - Start the Go mock server on port 8080
   - Start the Flask backend on port 5000
   - Start the React frontend on port 3000

4. **Access the Dashboard**
   - Open [http://localhost:3000](http://localhost:3000) in your browser.
   - Log in with any allowed phone number (see `test_data_dir/` for options).

---

## Technologies Used

| Component         | Technology   | Purpose                                              |
|-------------------|-------------|------------------------------------------------------|
| Go Server         | Go          | Mock Fi-mcp API, serves dummy financial data          |
| Flask Backend     | Python/Flask| Aggregates data, integrates with Gemini for AI advice |
| React Frontend    | React/JS    | User dashboard, charts, and recommendations UI        |

---

## Customization

- **Add More Dummy Data:**
  - Place new JSON files in each user's directory under `test_data_dir/`.
  - Update `DATA_ENDPOINTS` in `flask-backend/app.py` to include new endpoints.
  - Add new sections to the React dashboard as needed.

- **Change Ports:**
  - Edit `run.sh` and the relevant server files if you need to use different ports.

---

## Troubleshooting

- If a server fails to start, check for missing dependencies and install them as prompted.
- If you see CORS errors, ensure all servers are running and ports are correct.
- To stop all servers, use the `kill` command with the process IDs printed by `run.sh`.

---

## FAQ

**Q: Where do I put my Gemini API key?**
A: In `flask-backend/app.py`, replace `YOUR_GEMINI_API_KEY` in the `GEMINI_API_URL` variable.

**Q: What phone numbers can I use to log in?**
A: Any directory name in `test_data_dir/` is a valid phone number for login.

**Q: Is this safe for demos?**
A: Yes, all data is static and there are no real integrations.

---

For further help, check the README or contact the project maintainer. 