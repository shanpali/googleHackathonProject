# FI-MCP Financial Intelligence Platform - API Documentation

## 📡 Complete API Endpoints Reference

### **Base URL**
```
http://localhost:5001
```

---

## 🔐 Authentication Endpoints

### **POST /login**
User login with phone number authentication.

**Request:**
```json
{
  "phone": "9876543210"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "phone": "9876543210"
}
```

**Error Response:**
```json
{
  "error": "Invalid phone number format"
}
```

---

### **GET /logout**
User logout and session termination.

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## 🤖 AI & Chatbot Endpoints

### **POST /chatbot**
AI-powered financial chatbot for natural language queries.

**Request:**
```json
{
  "message": "Can I retire at 50?",
  "chat_history": [
    {
      "role": "user",
      "content": "What's my current financial health?"
    },
    {
      "role": "assistant", 
      "content": "Based on your financial data..."
    }
  ]
}
```

**Response:**
```json
{
  "response": "Based on your current financial situation, retiring at 50 would require...",
  "analysis_type": "retirement_planning",
  "recommendations": [
    {
      "title": "Increase Emergency Fund",
      "description": "Build 6 months of expenses",
      "priority": "High"
    }
  ],
  "confidence_score": 0.85
}
```

---

### **POST /adk/analyze**
ADK-compliant financial analysis endpoint.

**Request:**
```json
{
  "message": "How should I invest my salary?",
  "financial_data": {
    "fetch_net_worth": {...},
    "fetch_bank_transactions": {...}
  },
  "chat_history": [],
  "user_profile": {
    "risk_tolerance": "moderate",
    "investment_goals": ["retirement", "tax_savings"]
  }
}
```

**Response:**
```json
{
  "response": "Based on your salary and financial profile...",
  "tools_used": ["analyze_portfolio", "calculate_tax_savings"],
  "confidence_score": 0.92,
  "analysis_type": "investment_strategy"
}
```

---

## 📊 Financial Health & Insights

### **GET /health-score**
Calculate comprehensive financial health score with 6 categories.

**Response:**
```json
{
  "score": 67.5,
  "category": "Good",
  "breakdown": {
    "Emergency Fund": 75.0,
    "Debt Management": 85.0,
    "Investment Allocation": 60.0,
    "Net Worth": 70.0,
    "Cash Flow": 55.0,
    "Portfolio Diversification": 65.0
  },
  "strengths": [
    "Good debt management",
    "Positive net worth",
    "Strong emergency fund coverage"
  ],
  "weaknesses": [
    "Low investment allocation",
    "Poor portfolio diversification"
  ],
  "recommendations": [
    "Increase investment allocation for better returns",
    "Rebalance portfolio for better diversification"
  ],
  "overall_analysis": "Your financial health score is 67.5/100..."
}
```

---

### **GET /insights**
Get proactive insights and alerts.

**Query Parameters:**
- `refresh=true` (optional): Force refresh of insights

**Response:**
```json
{
  "insights": [
    {
      "title": "Salary Credit Analysis",
      "priority": "Informational",
      "description": "Your average monthly salary is ₹81,250. Salary consistency is 97.2%.",
      "action": "View salary trends",
      "save": "Financial planning",
      "icon": "income"
    },
    {
      "title": "EMI Payment Alert",
      "priority": "High Priority",
      "description": "You have ₹28,000 in EMI payments due this month.",
      "action": "Review EMI schedule",
      "save": "Avoid late fees",
      "icon": "alert"
    },
    {
      "title": "Tax Optimization Required",
      "priority": "High Priority",
      "description": "Invest ₹1,50,000 in ELSS by June 15th to save ₹45,000 in taxes.",
      "action": "Take Action",
      "save": "Save ₹45,000",
      "icon": "tax"
    }
  ]
}
```

---

### **POST /insights**
Get goal-specific insights.

**Request:**
```json
{
  "goals": [
    {
      "id": "goal_123",
      "title": "Buy a House",
      "target_amount": 5000000,
      "target_date": "2027-12-31"
    }
  ]
}
```

**Response:**
```json
{
  "insights": [
    {
      "title": "Goal Progress Alert",
      "priority": "Medium Priority",
      "description": "You're 45% towards your house goal. Consider increasing monthly savings.",
      "action": "Review goal progress",
      "save": "Achieve goal faster",
      "icon": "goal"
    }
  ]
}
```

---

## 💡 Recommendations & Portfolio

### **GET /recommendations**
Get personalized financial recommendations.

**Response:**
```json
{
  "recommendations": [
    {
      "title": "Start SIP in Index Funds",
      "description": "Begin systematic investment of ₹10,000 monthly in Nifty 50 index funds.",
      "priority": "High",
      "action": "Set up SIP",
      "expected_return": "12-15% annually"
    },
    {
      "title": "Optimize Tax Savings",
      "description": "Invest ₹1.5L in ELSS funds to maximize 80C benefits.",
      "priority": "High",
      "action": "Invest in ELSS",
      "tax_savings": "₹45,000"
    }
  ]
}
```

---

### **GET /portfolio**
Get portfolio analysis and asset allocation.

**Response:**
```json
{
  "portfolio": {
    "equity_allocation": 45.5,
    "debt_allocation": 35.2,
    "cash_allocation": 19.3,
    "net_worth": 2500000,
    "total_investments": 2000000,
    "emergency_fund": 300000,
    "risk_score": 7.2,
    "expected_return": 11.5
  },
  "breakdown": {
    "mutual_funds": 1200000,
    "stocks": 500000,
    "bonds": 300000,
    "cash": 400000
  }
}
```

---

## 🎯 Goals Management

### **GET /goals**
Get user's financial goals.

**Response:**
```json
{
  "goals": [
    {
      "id": "goal_123",
      "title": "Buy a House",
      "target_amount": 5000000,
      "target_date": "2027-12-31",
      "current_amount": 2250000,
      "progress": 45.0,
      "description": "Down payment for dream home",
      "monthly_contribution": 50000,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### **POST /goals**
Create new financial goal.

**Request:**
```json
{
  "title": "Emergency Fund",
  "target_amount": 300000,
  "target_date": "2024-12-31",
  "description": "Build 6 months emergency fund"
}
```

**Response:**
```json
{
  "success": true,
  "goal": {
    "id": "goal_456",
    "title": "Emergency Fund",
    "target_amount": 300000,
    "target_date": "2024-12-31",
    "current_amount": 0,
    "progress": 0.0,
    "description": "Build 6 months emergency fund"
  }
}
```

---

### **PUT /goals/<goal_id>**
Update existing goal.

**Request:**
```json
{
  "title": "Emergency Fund",
  "target_amount": 400000,
  "target_date": "2024-12-31",
  "description": "Build 8 months emergency fund"
}
```

**Response:**
```json
{
  "success": true,
  "goal": {
    "id": "goal_456",
    "title": "Emergency Fund",
    "target_amount": 400000,
    "target_date": "2024-12-31",
    "current_amount": 150000,
    "progress": 37.5
  }
}
```

---

### **DELETE /goals/<goal_id>**
Delete financial goal.

**Response:**
```json
{
  "success": true,
  "message": "Goal deleted successfully"
}
```

---

### **GET /goal-suggestions**
Get AI-generated goal suggestions.

**Response:**
```json
{
  "suggestions": [
    {
      "title": "Emergency Fund",
      "description": "Build 6 months of expenses as emergency fund",
      "target_amount": 300000,
      "reasoning": "Based on your monthly expenses of ₹50,000",
      "priority": "High"
    },
    {
      "title": "Tax-Saving Investment",
      "description": "Invest in ELSS funds for tax benefits",
      "target_amount": 150000,
      "reasoning": "Maximize 80C deductions",
      "priority": "Medium"
    }
  ]
}
```

---

## 💰 Lending System ("Udhaar Aur Bharosa")

### **POST /udhaar/voice-analyze**
Analyze voice recording for lending information.

**Request:**
```json
{
  "audio_data": "base64_encoded_audio_string"
}
```

**Response:**
```json
{
  "transcript": "I lent ₹20,000 to Rahul for his business",
  "borrower_name": "Rahul",
  "borrower_phone": null,
  "amount": 20000,
  "purpose": "business",
  "due_date": null,
  "confidence": 0.85
}
```

---

### **POST /udhaar/lend**
Create new lending entry.

**Request:**
```json
{
  "borrower_name": "Rahul",
  "borrower_phone": "9876543210",
  "amount": 20000,
  "description": "Business loan",
  "due_date": "2024-12-31"
}
```

**Response:**
```json
{
  "success": true,
  "lending_id": "lend_789",
  "message": "Lending entry created successfully"
}
```

---

### **POST /udhaar/repay**
Record loan repayment.

**Request:**
```json
{
  "lending_id": "lend_789",
  "amount": 20000
}
```

**Response:**
```json
{
  "success": true,
  "message": "Repayment recorded successfully"
}
```

---

### **GET /udhaar/lendings**
Get all lending transactions.

**Response:**
```json
{
  "lendings": [
    {
      "id": "lend_789",
      "borrower_name": "Rahul",
      "borrower_phone": "9876543210",
      "amount": 20000,
      "description": "Business loan",
      "due_date": "2024-12-31",
      "status": "active",
      "trust_rating": 8.5,
      "trust_level": "excellent",
      "created_at": "2024-01-15T10:30:00Z",
      "repaid_at": null
    }
  ]
}
```

---

### **GET /udhaar/trust-rating/<borrower_phone>**
Get borrower trust rating.

**Response:**
```json
{
  "trust_rating": 8.5,
  "trust_level": "excellent",
  "lending_history": [
    {
      "amount": 20000,
      "status": "repaid",
      "repayment_date": "2024-01-20T15:30:00Z"
    }
  ],
  "total_lent": 50000,
  "total_repaid": 50000,
  "repayment_rate": 100.0
}
```

---

### **POST /udhaar/lending-analysis**
Comprehensive lending analysis with financial context.

**Request:**
```json
{
  "borrower_phone": "9876543210",
  "amount": 50000
}
```

**Response:**
```json
{
  "affordability_score": 75.0,
  "risk_level": "moderate",
  "recommendation": "proceed_with_caution",
  "analysis": "You can afford this lending amount...",
  "financial_metrics": {
    "cash_after_lending": 150000,
    "emergency_fund_ratio": 3.0,
    "goals_impact": "minimal"
  },
  "trust_analysis": {
    "trust_score": 8.5,
    "repayment_history": "excellent",
    "risk_assessment": "low"
  }
}
```

---

## 🤖 ADK (Agent Development Kit) Endpoints

### **GET /adk/info**
Get ADK agent information.

**Response:**
```json
{
  "name": "Custom Financial Advisor Agent",
  "version": "1.0",
  "description": "Advanced AI-powered financial analysis with Indian context",
  "capabilities": [
    "portfolio_analysis",
    "tax_optimization",
    "lending_analysis",
    "goal_planning"
  ],
  "tools": [...],
  "schema": {...},
  "adk_compliant": true
}
```

---

### **GET /adk/compliance**
Check ADK compliance.

**Response:**
```json
{
  "compliant": true,
  "tools": [
    "analyze_portfolio",
    "calculate_tax_savings",
    "assess_lending_affordability"
  ],
  "schema": {
    "type": "object",
    "properties": {...}
  }
}
```

---

### **GET /adk/tools**
Get ADK tool definitions.

**Response:**
```json
{
  "tools": [
    {
      "name": "analyze_portfolio",
      "description": "Analyze portfolio allocation and suggest optimizations",
      "parameters": {
        "type": "object",
        "properties": {
          "risk_tolerance": {"type": "string"},
          "investment_goals": {"type": "array"}
        }
      }
    }
  ]
}
```

---

### **GET /adk/schema**
Get ADK response schema.

**Response:**
```json
{
  "schema": {
    "type": "object",
    "properties": {
      "response": {"type": "string"},
      "analysis_type": {"type": "string"},
      "tools_used": {"type": "array"},
      "confidence_score": {"type": "number"}
    }
  }
}
```

---

### **POST /adk/function-call**
Execute ADK function call.

**Request:**
```json
{
  "function_name": "analyze_portfolio",
  "args": {
    "risk_tolerance": "moderate",
    "investment_goals": ["retirement", "tax_savings"]
  }
}
```

**Response:**
```json
{
  "function_name": "analyze_portfolio",
  "result": {
    "allocation": {
      "equity": 60,
      "debt": 30,
      "cash": 10
    },
    "recommendations": [...]
  },
  "success": true
}
```

---

## 📊 Data Export & Analytics

### **GET /export-data**
Export comprehensive financial data.

**Response:**
```json
{
  "net_worth": {
    "total": 2500000,
    "breakdown": {
      "investments": 2000000,
      "cash": 500000
    }
  },
  "transactions": [
    {
      "amount": 80000,
      "description": "Salary Credit",
      "date": "2024-01-01",
      "type": "credit"
    }
  ],
  "portfolio": {
    "equity_allocation": 45.5,
    "debt_allocation": 35.2,
    "cash_allocation": 19.3
  },
  "insights": [...],
  "goals": [...]
}
```

---

### **GET /recent-transactions**
Get recent financial transactions.

**Response:**
```json
{
  "transactions": [
    {
      "amount": 80000,
      "description": "Salary Credit",
      "date": "2024-01-01",
      "type": "credit",
      "category": "income"
    },
    {
      "amount": -15000,
      "description": "Home Loan EMI",
      "date": "2024-01-01",
      "type": "debit",
      "category": "loan_payment"
    }
  ]
}
```

---

## 🔧 Error Handling

### **Standard Error Response Format**
```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### **Common Error Codes**
- `400` - Bad Request (Invalid input)
- `401` - Unauthorized (Not logged in)
- `403` - Forbidden (Insufficient permissions)
- `404` - Not Found (Resource not found)
- `500` - Internal Server Error (Server error)

---

## 📝 Usage Examples

### **Complete Workflow Example**

1. **Login:**
```bash
curl -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "9876543210"}'
```

2. **Get Financial Health:**
```bash
curl -X GET http://localhost:5001/health-score \
  -H "Content-Type: application/json"
```

3. **Ask AI Question:**
```bash
curl -X POST http://localhost:5001/chatbot \
  -H "Content-Type: application/json" \
  -d '{"message": "How should I invest my salary?"}'
```

4. **Create Goal:**
```bash
curl -X POST http://localhost:5001/goals \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Emergency Fund",
    "target_amount": 300000,
    "target_date": "2024-12-31",
    "description": "Build 6 months emergency fund"
  }'
```

5. **Record Lending:**
```bash
curl -X POST http://localhost:5001/udhaar/lend \
  -H "Content-Type: application/json" \
  -d '{
    "borrower_name": "Rahul",
    "amount": 20000,
    "description": "Business loan",
    "due_date": "2024-12-31"
  }'
```

---

## 🚀 Performance Notes

- **Response Time:** Most endpoints respond within 1-2 seconds
- **AI Analysis:** Complex queries may take 3-5 seconds
- **Voice Processing:** Audio analysis takes 5-10 seconds
- **Rate Limiting:** 100 requests per minute per user
- **Session Timeout:** 24 hours of inactivity

---

*This API documentation covers all endpoints in the FI-MCP Financial Intelligence Platform. For additional support, refer to the project summary or contact the development team.* 