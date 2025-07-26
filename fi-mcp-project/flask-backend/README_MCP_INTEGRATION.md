# MCP Client Integration Guide

This document explains the updated MCP (Model Context Protocol) client integration with your Flask backend and Gemini AI service.

## What Was Fixed

### Previous Issues
- The old MCP client was trying to call HTTP endpoints like `/tools` which don't exist in proper MCP servers
- MCP servers use stdio (standard input/output) communication, not HTTP REST APIs
- Tools weren't being properly passed to Gemini AI

### Current Solution
- Proper MCP client using the stdio protocol as per MCP specification
- Automatic tool registration with Gemini AI service
- Support for multiple MCP servers
- Async tool execution with proper error handling

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gemini AI     │    │  MCP Client     │    │   MCP Server    │
│                 │    │                 │    │   (Go/Other)    │
│ - Tool calling  │◄──►│ - Tool registry │◄──►│ - Tool impl.    │
│ - Text gen.     │    │ - Stdio comm.   │    │ - stdio        │
│ - Function exec │    │ - Format conv.  │    │ - JSON-RPC      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Files Modified

### 1. `mcp_client.py`
- **Complete rewrite** to use proper MCP stdio protocol
- Added support for multiple servers
- Automatic tool discovery and registration
- Conversion between MCP and Gemini tool formats
- Async tool execution

### 2. `gemini_service.py`
- Added MCP client integration in `__init__`
- Automatic MCP tool registration with tool registry
- Support for async tool execution from Gemini
- Enhanced function call handling

### 3. `mcp_config.json`
- Updated format from URL-based to command-based
- Now specifies actual commands to run MCP servers

### 4. `app.py`
- Added `/mcp-tools` endpoint for debugging
- Enhanced error handling

## Configuration

### MCP Server Configuration (`mcp_config.json`)

```json
{
    "mcpServers": {
        "fi_mcp": {
            "command": "go",
            "args": ["run", "../../../fi-mcp-dev/main.go"]
        },
        "another_server": {
            "command": "python",
            "args": ["path/to/server.py"]
        }
    }
}
```

### Server Formats Supported
- **Go servers**: `{"command": "go", "args": ["run", "main.go"]}`
- **Python servers**: `{"command": "python", "args": ["server.py"]}`
- **Node.js servers**: `{"command": "node", "args": ["server.js"]}`

## Usage

### 1. Testing MCP Connection

```bash
cd flask-backend
python test_mcp_client.py
```

### 2. API Endpoints

#### Get Available Tools
```http
GET /mcp-tools
```

Response:
```json
{
    "raw_tools": {
        "fi_mcp": [
            {
                "name": "fetch_bank_transactions",
                "description": "Fetch bank transaction data",
                "input_schema": {...},
                "server": "fi_mcp"
            }
        ]
    },
    "gemini_tools": [
        {
            "name": "fi_mcp_fetch_bank_transactions",
            "description": "Fetch bank transaction data",
            "parameters": {...}
        }
    ],
    "success": true
}
```

### 3. Chatbot Integration

The chatbot automatically has access to all MCP tools:

```http
POST /chatbot
{
    "message": "Show me my recent bank transactions"
}
```

Gemini will automatically:
1. See available MCP tools
2. Choose appropriate tool (`fi_mcp_fetch_bank_transactions`)
3. Execute the tool via MCP client
4. Use results in the response

## Tool Naming Convention

MCP tools are prefixed with server name to avoid conflicts:
- Server: `fi_mcp`, Tool: `fetch_bank_transactions`
- Gemini sees: `fi_mcp_fetch_bank_transactions`

## Error Handling

### Common Issues & Solutions

1. **"Server connection failed"**
   - Check if MCP server is running
   - Verify command/args in config
   - Check file paths are correct

2. **"Tool execution failed"**
   - MCP server may have crashed
   - Check server logs
   - Verify tool arguments

3. **"No MCP servers available"**
   - Check `mcp_config.json` exists
   - Verify server configurations
   - Check network connectivity

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Gemini

### Automatic Tool Registration
When `GeminiService` initializes:
1. Connects to all MCP servers
2. Discovers available tools
3. Converts to Gemini format
4. Registers with tool registry

### Tool Execution Flow
1. User asks question to Gemini
2. Gemini decides to use MCP tool
3. `GeminiService` calls MCP client
4. MCP client executes tool on server
5. Result returned to Gemini
6. Gemini incorporates result in response

## Best Practices

1. **Server Management**
   - Keep MCP servers lightweight
   - Handle server restarts gracefully
   - Monitor server health

2. **Tool Design**
   - Clear, descriptive tool names
   - Comprehensive parameter schemas
   - Good error messages

3. **Performance**
   - Cache tool lists when possible
   - Use async operations
   - Handle timeouts properly

## Troubleshooting

### Check MCP Server
```bash
# Test if your Go MCP server works
cd fi-mcp-dev
go run main.go
```

### Check Tool Discovery
```bash
# Test tool discovery
cd flask-backend
python -c "from mcp_client import MCPClient; client = MCPClient(); print(client.get_all_available_tools_sync())"
```

### Check Gemini Integration
```bash
# Test full integration
curl -X GET http://localhost:5000/mcp-tools
```

## Next Steps

1. **Test the integration** with your Go MCP server
2. **Add more tools** to your MCP server as needed
3. **Monitor performance** and add caching if needed
4. **Handle edge cases** like server crashes or network issues

The integration now follows proper MCP protocols and should work seamlessly with your existing Gemini AI service while providing access to all tools from your MCP servers.
