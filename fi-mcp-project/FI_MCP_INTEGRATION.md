# 🔐 FI-MCP Server Integration

## Overview

This document describes the integration with the FI-MCP (Financial Information Model Context Protocol) server, which provides real financial data instead of mock data.

## Server Details

- **URL**: `http://localhost:8484/mcp/stream`
- **Protocol**: JSON-RPC 2.0
- **Authentication**: Required via web-based OTP flow
- **Session Management**: Uses `Mcp-Session-Id` header

## Authentication Flow

### 1. Frontend Integration

The dashboard now includes a "Connect to Real Data" button that:

1. **Initiates Authentication**: Calls `/fi-mcp-auth` endpoint
2. **Shows Login URL**: Displays authentication URL to user
3. **User Authentication**: User opens URL in new tab and enters OTP
4. **Retry with Real Data**: User clicks "Retry" to fetch authenticated data

### 2. Backend Endpoints

#### `/fi-mcp-auth` (POST)
- **Purpose**: Initiate fi-mcp authentication
- **Response**: Returns login URL for user authentication
- **Example Response**:
```json
{
  "status": "auth_required",
  "session_id": "mcp-session-xxx",
  "login_url": "http://localhost:8484/mockWebPage?sessionId=xxx",
  "message": "Please authenticate with fi-mcp server"
}
```

#### `/fi-mcp-retry` (POST)
- **Purpose**: Retry data fetch after authentication
- **Response**: Returns real financial data if authenticated
- **Example Response**:
```json
{
  "status": "success",
  "data": { /* real financial data */ },
  "message": "Successfully fetched real data from fi-mcp server"
}
```

### 3. User Experience Flow

1. **Dashboard Load**: User sees "Connect to Real Data" button
2. **Click Connect**: User clicks button to start authentication
3. **Authentication Dialog**: Dialog opens with login URL
4. **Open URL**: User clicks link to open authentication page
5. **Enter OTP**: User enters OTP on fi-mcp authentication page
6. **Return to Dashboard**: User returns to dashboard
7. **Click Retry**: User clicks "Retry with Real Data" button
8. **Real Data Loaded**: Dashboard now shows real financial data

## Data Types Available

The fi-mcp server provides the following data types:

- `fetch_bank_transactions` - Bank account transactions
- `fetch_net_worth` - Net worth and asset allocation
- `fetch_credit_report` - Credit report data
- `fetch_epf_details` - EPF account details
- `fetch_insurance` - Insurance coverage data
- `fetch_mf_transactions` - Mutual fund transactions
- `fetch_stock_transactions` - Stock trading data

## Fallback Mechanism

If the fi-mcp server is unavailable or authentication fails:

1. **Graceful Fallback**: System falls back to mock data
2. **User Notification**: Status messages inform user of data source
3. **Seamless Experience**: All features continue to work with mock data

## Testing the Integration

### **Test Server Connectivity**
```bash
curl -X POST http://localhost:8484/mcp/stream \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: mcp-session-594e48ea-fea1-40ef-8c52-7552dd9272af" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "fetch_bank_transactions",
      "arguments": {}
    }
  }'
```

### **Test Flask Authentication Endpoint**
```bash
curl -X POST http://localhost:5001/fi-mcp-auth \
  -H "Content-Type: application/json" \
  -d '{}' \
  -b "session=your_session_cookie"
```

### **Test Flask Retry Endpoint**
```bash
curl -X POST http://localhost:5001/fi-mcp-retry \
  -H "Content-Type: application/json" \
  -d '{}' \
  -b "session=your_session_cookie"
```

## Frontend Components

### Dashboard Authentication Section

The dashboard now includes an authentication section that:

- **Visual Design**: Clean, prominent section with authentication button
- **Status Feedback**: Real-time status updates during authentication
- **Error Handling**: Clear error messages for failed authentication
- **Success States**: Confirmation when real data is loaded

### Authentication Dialog

A modal dialog that:

- **Login URL Display**: Shows the authentication URL as a clickable link
- **Instructions**: Clear step-by-step instructions for the user
- **Retry Button**: Allows user to retry data fetch after authentication
- **Loading States**: Shows loading indicators during data fetch

## Error Handling

### Common Error Scenarios

1. **Server Unavailable**: Graceful fallback to mock data
2. **Authentication Failed**: Clear error messages to user
3. **Session Expired**: Automatic session refresh
4. **Network Issues**: Retry mechanisms with exponential backoff

### User Feedback

- **Loading States**: Spinners and progress indicators
- **Status Messages**: Clear, informative status updates
- **Error Messages**: User-friendly error descriptions
- **Success Confirmations**: Positive feedback for successful operations

## Security Considerations

1. **Session Management**: Secure session handling with proper timeouts
2. **URL Validation**: Validation of authentication URLs
3. **Data Privacy**: Secure handling of financial data
4. **HTTPS**: All communications should use HTTPS in production

## Future Enhancements

1. **Automatic Authentication**: Seamless background authentication
2. **Persistent Sessions**: Long-term session management
3. **Real-time Updates**: Live data updates from fi-mcp server
4. **Advanced Error Recovery**: Sophisticated retry mechanisms 