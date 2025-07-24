# Enhanced Gemini AI Integration with Context Awareness

This module provides a comprehensive, modular integration with Google's Gemini AI for financial applications **with full context awareness of existing user data**.

## Key Features

- **Context-Aware AI**: Gemini knows about existing reminders, goals, alerts, and financial data
- **Modular Design**: Single service class that can be easily integrated into any Flask application
- **Smart Recommendations**: Avoids duplicates and provides complementary advice based on existing user state
- **Environment Configuration**: Secure API key management using environment variables  
- **Function Tools**: Built-in financial tools (reminders, reports, goals, alerts)
- **Production Ready**: Proper error handling, logging, and configuration management

## Why Function Tools Over Internal MCP?

**Our Choice: Function Tools**

### ✅ **Perfect for Your App Because:**
- **Direct Integration**: Functions run in the same Flask process, sharing user sessions and database connections
- **Context Sharing**: Easy access to existing user reminders, goals, and financial data
- **Performance**: No network latency - everything runs locally
- **Simpler Deployment**: One service to deploy and monitor
- **Easier Testing**: Unit test functions independently

### 🤔 **MCP Would Add Complexity:**
- Separate authentication between Flask app and MCP server
- Data synchronization challenges between services  
- Additional network calls and potential latency
- More complex deployment and monitoring

### 📊 **Context Awareness Advantage:**
With Function Tools, when a user asks "Help me set a savings goal", Gemini can see:
- Existing goals: "You already have an Emergency Fund goal at 60% completion"
- Current reminders: "You have a portfolio review scheduled for next week"
- Financial state: "Based on your $2,500 monthly surplus, here's what's realistic"

## Enhanced Context System

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-pro
DEFAULT_SYSTEM_INSTRUCTION=You are a professional financial advisor...
```

### **Context-Aware Methods**

```python
from gemini_service import get_gemini_service

service = get_gemini_service()

# Context-aware query (recommended for user interactions)
response = service.generate_content_with_user_context(
    user_content="Should I increase my emergency fund?",
    phone="user_phone_number",
    financial_data=user_financial_data
)

# Context-aware recommendations 
recommendations = service.generate_recommendations(
    user_data=financial_data,
    phone="user_phone_number",
    focus_areas=["goal_optimization"]
)
```

### **What Context Includes:**

- **Existing Reminders**: "Pay credit card bill on July 30th"
- **Active Goals**: "Emergency Fund: $15,000 / $25,000 (60%) - Target: Dec 2025"
- **Investment Alerts**: "AAPL price alert above $200"
- **Financial Data**: Net worth, recent transactions, investment holdings
- **Current Date**: For time-sensitive advice

## Usage Examples

### **Before (Without Context)**
```
User: "Help me set a savings goal"
AI: "I'd recommend setting an emergency fund goal of $25,000..."
```

### **After (With Context)**  
```
User: "Help me set a savings goal"
AI: "I see you already have an Emergency Fund goal that's 60% complete ($15,000/$25,000). 
     Since you're on track with that, let's consider a vacation fund or house down payment goal..."
```

## Architecture Decisions

### Function Tools vs Internal MCP

**Recommendation: Use Function Tools (Current Implementation)**

**Why Function Tools:**
- ✅ **Simplicity**: Easier to implement and maintain
- ✅ **Performance**: Lower latency as functions execute locally
- ✅ **Control**: Full control over function execution and error handling
- ✅ **Testing**: Easier to unit test individual functions
- ✅ **Deployment**: No need for separate MCP server infrastructure

**When to Consider Internal MCP:**
- 🤔 **Scale**: If you have 20+ complex tools
- 🤔 **Isolation**: If tools need to run in separate processes
- 🤔 **Reusability**: If tools need to be shared across multiple applications
- 🤔 **Security**: If tools need stricter sandboxing

**Current Implementation Benefits:**
- Functions are registered dynamically
- Easy to add new tools by implementing functions
- Direct integration with Flask application
- Shared context and database connections

## Available Tools

### 1. Schedule Reminder
```python
# Example: "Remind me to pay my credit card bill on July 30th at 9 AM"
{
    "name": "schedule_reminder",
    "parameters": {
        "title": "Pay credit card bill",
        "date": "2025-07-30", 
        "time": "09:00",
        "category": "payment"
    }
}
```

### 2. Generate Financial Report
```python
# Example: "Generate a monthly report including net worth and investments"
{
    "name": "generate_financial_report",
    "parameters": {
        "report_type": "monthly",
        "include_sections": ["net_worth", "investments"]
    }
}
```

### 3. Set Financial Goal
```python
# Example: "I want to save $50,000 for a house by December 2026"
{
    "name": "set_financial_goal", 
    "parameters": {
        "goal_name": "House Down Payment",
        "target_amount": 50000,
        "target_date": "2026-12-31",
        "priority": "high",
        "category": "house"
    }
}
```

### 4. Create Investment Alert
```python
# Example: "Alert me when AAPL goes above $200"
{
    "name": "create_investment_alert",
    "parameters": {
        "alert_type": "price_target",
        "asset_symbol": "AAPL", 
        "condition": "price above 200"
    }
}
```

## Adding Custom Tools

### 1. Define Function Schema
```python
custom_tool = {
    "name": "your_function_name",
    "description": "What this function does",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    }
}
```

### 2. Implement Function
```python
def your_function_implementation(param1: str) -> Dict[str, Any]:
    # Your implementation here
    return {"success": True, "result": "Function executed"}
```

### 3. Register Function
```python
service = get_gemini_service()
service.register_function("your_function_name", your_function_implementation)
```

## API Endpoints

### `/chatbot` (POST)
Interactive chat with AI assistant including tool capabilities.

**Request:**
```json
{
    "message": "Help me create a budget for next month"
}
```

**Response:**
```json
{
    "response": "I'd be happy to help you create a budget...",
    "function_calls": [...],
    "history": [...],
    "success": true
}
```

### `/recommendations` (GET)
Generate personalized financial recommendations based on user data.

**Response:**
```json
{
    "recommendations": "Based on your financial data, here are my recommendations...",
    "function_calls": [...],
    "success": true
}
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | Required | Your Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-pro` | Primary model for complex queries |
| `GEMINI_FLASH_MODEL` | `gemini-2.5-flash` | Faster model for simple queries |
| `DEFAULT_SYSTEM_INSTRUCTION` | Financial advisor prompt | Default AI behavior |

## Error Handling

The service includes comprehensive error handling:
- API key validation on startup
- Graceful function execution failures
- Proper HTTP status codes
- Detailed error logging

## Production Considerations

1. **Security**: Store API keys in secure environment variables
2. **Rate Limiting**: Implement rate limiting for API calls
3. **Caching**: Consider caching responses for repeated queries
4. **Monitoring**: Add monitoring for function execution and API usage
5. **Database**: Replace file-based storage with proper database
6. **Authentication**: Implement proper user authentication and authorization

## Extending the System

The modular design makes it easy to extend:

1. **Add New Tools**: Simply implement function and register it
2. **Custom Models**: Configure different models for different use cases  
3. **Enhanced Context**: Add more sophisticated context management
4. **Multi-tenancy**: Add user-specific configurations and data isolation
