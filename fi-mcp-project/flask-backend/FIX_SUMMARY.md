# 🐛 Fix Applied: Async/Sync Coroutine Issue

## Problem Diagnosed
The chatbot was failing with the error:
```
"error": "Chat processing failed: Object of type coroutine is not JSON serializable"
```

And the backend logs showed:
```
RuntimeWarning: coroutine 'GeminiService._register_mcp_tools.<locals>.create_mcp_wrapper.<locals>.mcp_tool_wrapper' was never awaited
```

## Root Cause
The MCP tool wrapper functions were defined as `async` functions (coroutines), but they were being called in a synchronous context by Gemini's tool execution system. When Gemini tried to execute these tools, it received a coroutine object instead of the actual result, which then couldn't be serialized to JSON.

## Solution Applied

### 1. Made MCP Tool Wrappers Synchronous
Changed the tool wrapper functions from async to sync, and added proper async execution handling:

```python
# BEFORE (Async wrapper causing issues)
async def mcp_tool_wrapper(**kwargs):
    return await self.mcp_client.execute_tool_for_gemini(tool_name, kwargs)

# AFTER (Sync wrapper with proper async handling)
def mcp_tool_wrapper(**kwargs):
    try:
        import asyncio
        # Check if there's already an event loop running
        try:
            loop = asyncio.get_running_loop()
            # If there's a running loop, run in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(self.mcp_client.execute_tool_for_gemini(tool_name, kwargs))
                )
                return future.result(timeout=30)
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(self.mcp_client.execute_tool_for_gemini(tool_name, kwargs))
    except Exception as e:
        return {"success": False, "error": str(e), "tool": tool_name}
```

### 2. Simplified Function Call Execution
Removed the async coroutine handling from `_execute_function_call` since all wrappers are now synchronous:

```python
# BEFORE
if asyncio.iscoroutine(result):
    result = asyncio.run(result)

# AFTER
# Removed - no longer needed since wrappers are sync
result = self.tool_registry.execute_function(function_name, **function_args)
```

### 3. Fixed MCP Server Configuration
Updated the MCP server URL to use the correct port (8080 instead of 8484):

```json
{
    "mcpServers": {
        "fi_mcp": {
            "url": "http://localhost:8080/mcp/stream"
        }
    }
}
```

## Test Results

✅ **MCP Tool Registration Test**: 6 MCP tools successfully registered  
✅ **Async/Sync Fix Test**: No more coroutine serialization errors  
✅ **Tool Execution Test**: Gemini can now execute MCP tools without async issues  

## Available MCP Tools for Gemini

The following tools are now properly registered and available to Gemini:
- `fi_mcp_fetch_bank_transactions`
- `fi_mcp_fetch_credit_report`
- `fi_mcp_fetch_net_worth`
- `fi_mcp_fetch_mf_transactions`
- `fi_mcp_fetch_stock_transactions`
- `fi_mcp_fetch_epf_details`

## How to Test

1. **Start your Go MCP server**:
   ```bash
   cd fi-mcp-dev
   go run main.go
   ```

2. **Start the Flask backend**:
   ```bash
   cd fi-mcp-project/flask-backend
   python app.py
   ```

3. **Test the chatbot**:
   ```bash
   # Login first
   curl -X POST -H 'Content-Type: application/json' \
        -d '{"phone": "1234567890"}' \
        -c cookies.txt \
        http://localhost:5000/login

   # Chat with financial questions
   curl -X POST -H 'Content-Type: application/json' \
        -d '{"message": "What is my net worth?"}' \
        -b cookies.txt \
        http://localhost:5000/chatbot
   ```

The async/sync issue is now resolved and the chatbot should work without JSON serialization errors! 🎉

## Files Modified
- `gemini_service.py`: Fixed async tool wrapper registration
- `mcp_config.json`: Updated to correct server port
- Added test files for verification
