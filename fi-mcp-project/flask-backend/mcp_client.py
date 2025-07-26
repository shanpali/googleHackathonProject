import asyncio
from typing import Optional, Dict, List, Any
from contextlib import AsyncExitStack
import json
import os
import logging
import requests
import subprocess
import time
import uuid
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self, config_path: str = "mcp_config.json"):
        # Initialize session and client objects
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
        self.config_path = config_path
        self.servers = self._load_config()
        self.connected_servers = {}
        self.server_processes = {}
        # Authentication state
        self.authenticated_sessions = {}  # Track authenticated sessions per server
        self.pending_auth = {}  # Track pending authentication flows
        self.session_timeout = 3600  # 1 hour session timeout (configurable)
        logger.info("init mcp client complete")

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"MCP config file not found: {self.config_path}")
        with open(self.config_path, "r") as f:
            config = json.load(f)
        # Expected format supports both stdio and HTTP servers
        servers = config.get("mcpServers", {})
        logger.info(f"servers: {servers}")
        return servers

    async def _start_server_process(self, server_name: str, server_config: dict):
        """Start the MCP server process if it's not already running."""
        try:
            if "command" in server_config:
                command = server_config["command"]
                args = server_config.get("args", [])
                
                # Start the server process
                process = subprocess.Popen(
                    [command] + args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.server_processes[server_name] = process
                
                # Give the server time to start
                time.sleep(2)
                
                # Check if process is still running
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    logger.error(f"Server {server_name} failed to start: {stderr}")
                    raise Exception(f"Server failed to start: {stderr}")
                
                logger.info(f"Started MCP server process for {server_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error starting server process {server_name}: {e}")
            return False

    async def connect_to_server(self, server_name: str, server_config: dict):
        """Connect to an MCP server using stdio or HTTP transport."""
        try:
            # Check if this is an HTTP-based server
            if "url" in server_config:
                # HTTP-based MCP server
                return await self._connect_http_server(server_name, server_config)
            elif "command" in server_config:
                # Stdio-based MCP server - start process first
                await self._start_server_process(server_name, server_config)
                return await self._connect_stdio_server(server_name, server_config)
            else:
                raise ValueError(f"Server config for {server_name} must have either 'command' or 'url'")

        except Exception as e:
            logger.error(f"Error connecting to MCP server {server_name}: {e}")
            raise

    async def _connect_http_server(self, server_name: str, server_config: dict):
        """Connect to HTTP-based MCP server (like your Go server)."""
        url = server_config["url"]
        
        # For HTTP MCP servers, we'll use a simple approach to get tools
        # This is a simplified implementation - a full HTTP MCP client would be more complex
        try:
            # Test if server is accessible
            response = requests.get(url.replace('/stream', '/health'), timeout=5)
            if response.status_code == 200:
                logger.info(f"HTTP MCP server {server_name} is accessible")
                self.connected_servers[server_name] = server_config
                return True
        except:
            # If health check fails, assume the basic URL is the MCP endpoint
            logger.info(f"Connected to HTTP MCP server {server_name} at {url}")
            self.connected_servers[server_name] = server_config
            return True

    async def _connect_stdio_server(self, server_name: str, server_config: dict):
        """Connect to stdio-based MCP server."""
        command = server_config["command"]
        args = server_config.get("args", [])

        # Create server parameters
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=None
        )

        # Connect to server
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio, write = stdio_transport
        session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )

        # Initialize the session
        await session.initialize()

        # Store the session
        self.sessions[server_name] = session
        self.connected_servers[server_name] = server_config

        logger.info(f"Connected to stdio MCP server: {server_name}")
        return session

    async def connect_to_all_servers(self):
        """Connect to all configured MCP servers."""
        for server_name, server_config in self.servers.items():
            try:
                await self.connect_to_server(server_name, server_config)
            except Exception as e:
                logger.error(f"Failed to connect to server {server_name}: {e}")

    async def get_server_tools(self, server_name: str) -> List[Dict]:
        """Get tools from a specific server."""
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} is not configured")
        
        server_config = self.servers[server_name]
        
        if "url" in server_config:
            # HTTP server - use streamable HTTP client to get actual tools
            try:
                async with streamablehttp_client(server_config['url']) as (
                    read_stream,
                    write_stream,
                    _,
                ):
                    async with ClientSession(
                        read_stream,
                        write_stream,
                    ) as session:
                        await session.initialize()
                        tools_response = await session.list_tools()
                        
                        # Convert MCP tool format to a more usable format
                        tools = []
                        for tool in tools_response.tools:
                            tool_info = {
                                "name": tool.name,
                                "description": tool.description,
                                "input_schema": tool.inputSchema,
                                "server": server_name
                            }
                            tools.append(tool_info)
                        
                        # Mark server as connected after successful tool retrieval
                        self.connected_servers[server_name] = server_config
                        logger.info(f"Successfully connected to HTTP MCP server: {server_name}")
                        return tools
            except Exception as e:
                logger.error(f"Error connecting to HTTP MCP server {server_name}: {e}")
                # Fallback to mock tools for local development
                return self._get_http_server_tools(server_name, server_config)
        else:
            # Stdio server
            if server_name not in self.sessions:
                # Connect if not already connected
                await self.connect_to_server(server_name, server_config)
            
            session = self.sessions[server_name]
            response = await session.list_tools()
            
            # Convert MCP tool format to a more usable format
            tools = []
            for tool in response.tools:
                tool_info = {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                    "server": server_name
                }
                tools.append(tool_info)
            
            return tools

    async def get_all_available_tools(self) -> Dict[str, List[Dict]]:
        """Returns a dict of available tools per server."""
        all_tools = {}
        
        # Go through all configured servers
        for server_name in self.servers.keys():
            try:
                tools = await self.get_server_tools(server_name)
                all_tools[server_name] = tools
                logger.info(f"Retrieved {len(tools)} tools from server {server_name}")
            except Exception as e:
                logger.error(f"Error getting tools from server {server_name}: {e}")
                all_tools[server_name] = []
        
        return all_tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on a specific server."""
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} is not configured")
        
        server_config = self.servers[server_name]
        
        if "url" in server_config:
            # HTTP server - make HTTP request to your existing endpoint
            return await self._call_http_tool(server_name, tool_name, arguments)
        else:
            # Stdio server
            if server_name not in self.sessions:
                # Connect if not already connected
                await self.connect_to_server(server_name, server_config)
            
            session = self.sessions[server_name]
            result = await session.call_tool(tool_name, arguments)
            return result

    async def generate_auth_session(self, server_name: str, phone_number: str) -> Dict[str, Any]:
        """Generate an authentication session and return the Fi Money login URL"""
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} is not configured")
        
        # First, try to get the login URL from the server by making a dummy tool call
        try:
            result = await self._call_http_tool(server_name, "fetch_net_worth", {}, use_dummy_session=True)
            
            # Check if we got a login_required response with login_url
            if isinstance(result, dict) and result.get("content"):
                content = result["content"]
                if isinstance(content, dict):
                    if content.get("status") == "login_required" and content.get("login_url"):
                        login_url = content["login_url"]
                        
                        # Extract session ID from the login URL
                        import re
                        session_match = re.search(r'token=(mcp-session-[^&]+)', login_url)
                        if session_match:
                            session_id = session_match.group(1)
                        else:
                            # Fallback to generating our own
                            session_id = f"mcp-session-{str(uuid.uuid4())}"
                        
                        # Store the pending authentication
                        self.pending_auth[server_name] = {
                            "session_id": session_id,
                            "phone_number": phone_number,
                            "status": "pending_auth_redirect",
                            "timestamp": time.time()
                        }
                        
                        logger.info(f"Generated auth session {session_id} for server {server_name}")
                        
                        return {
                            "success": True,
                            "session_id": session_id,
                            "login_url": login_url,
                            "message": content.get("message", "Please complete authentication at Fi Money using the provided link")
                        }
        except Exception as e:
            logger.info(f"Could not get login URL from server, generating fallback: {e}")
        
        # Fallback: generate our own session ID and URL
        session_id = f"mcp-session-{str(uuid.uuid4())}"
        
        # Store the pending authentication
        self.pending_auth[server_name] = {
            "session_id": session_id,
            "phone_number": phone_number,
            "status": "pending_auth_redirect",
            "timestamp": time.time()
        }
        
        # Get the base domain from server config
        server_config = self.servers[server_name]
        mcp_url = server_config["url"]  # e.g., "http://localhost:8484/mcp/stream"
        
        # Extract domain from MCP URL (remove mcp. prefix and port/path)
        # https://mcp.fi.money:8080/mcp/stream -> fi.money
        import re
        domain_match = re.search(r'://(?:mcp\.)?([^:/]+)', mcp_url)
        if domain_match:
            base_domain = domain_match.group(1)
            # Remove port if present
            base_domain = base_domain.split(':')[0]
        else:
            base_domain = "fi.money"  # fallback
        
        # Create the Fi Money login URL
        login_url = f"https://{base_domain}/wealth-mcp-login?token={session_id}"
        
        logger.info(f"Generated fallback auth session {session_id} for server {server_name}")
        
        return {
            "success": True,
            "session_id": session_id,
            "login_url": login_url,
            "message": "Please complete authentication using the provided link"
        }

    def mark_session_authenticated(self, server_name: str, session_id: str = None) -> Dict[str, Any]:
        """Mark a session as authenticated after successful Fi Money login"""
        
        # If no session_id provided, try to find it from pending auth
        if session_id is None:
            if server_name not in self.pending_auth:
                return {
                    "success": False,
                    "error": "No pending authentication session found and no session ID provided"
                }
            session_id = self.pending_auth[server_name]["session_id"]
        
        # Check if we have a pending session for this session_id
        if server_name not in self.pending_auth:
            return {
                "success": False,
                "error": "No pending authentication session found"
            }
        
        pending_session = self.pending_auth[server_name]
        if pending_session["session_id"] != session_id:
            return {
                "success": False,
                "error": "Session ID mismatch"
            }
        
        # For HTTP servers (like local Go server), register the session with the server
        server_config = self.servers.get(server_name, {})
        if "url" in server_config:
            try:
                # Extract base URL from MCP stream URL
                base_url = server_config["url"].replace("/mcp/stream", "")
                login_url = f"{base_url}/login"
                
                # Register session with the server
                login_data = {
                    "sessionId": session_id,
                    "phoneNumber": pending_session.get("phone_number", "unknown")
                }
                
                logger.info(f"Registering session {session_id} with server at {login_url}")
                response = requests.post(login_url, data=login_data, timeout=10)
                
                if response.status_code != 200:
                    logger.error(f"Failed to register session with server: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"Failed to register session with server: {response.text}"
                    }
                    
                logger.info(f"Successfully registered session {session_id} with server")
                
            except Exception as e:
                logger.error(f"Error registering session with server: {e}")
                return {
                    "success": False,
                    "error": f"Error registering session: {str(e)}"
                }
        
        # Move session from pending to authenticated
        import time
        self.authenticated_sessions[server_name] = {
            "session_id": session_id,
            "phone_number": pending_session.get("phone_number", "unknown"),
            "status": "authenticated",
            "timestamp": time.time(),
            "expires_in": self.session_timeout
        }
        
        # Remove from pending
        del self.pending_auth[server_name]
        
        logger.info(f"Session {session_id} authenticated for server {server_name}")
        
        return {
            "success": True,
            "message": "Session authenticated successfully",
            "session_id": session_id
        }

    async def _authenticate_http_server(self, server_name: str, phone_number: str) -> Dict[str, Any]:
        """Authenticate with HTTP MCP server by simulating the web login flow"""
        try:
            server_config = self.connected_servers[server_name]
            base_url = server_config["url"].replace("/mcp/stream", "")  # Get base server URL
            
            # Generate a session ID for this authentication attempt
            session_id = f"mcp-session-{str(uuid.uuid4())}"
            
            # Store the pending authentication
            self.pending_auth[server_name] = {
                "session_id": session_id,
                "phone_number": phone_number,
                "status": "pending"
            }
            
            # Simulate the login process by calling the login endpoint directly
            login_url = f"{base_url}/login"
            login_data = {
                "sessionId": session_id,
                "phoneNumber": phone_number
            }
            
            response = requests.post(login_url, data=login_data, timeout=10)
            
            if response.status_code == 200:
                # Authentication successful
                import time
                self.authenticated_sessions[server_name] = {
                    "session_id": session_id,
                    "phone_number": phone_number,
                    "status": "authenticated",
                    "timestamp": time.time(),  # Add timestamp for expiry
                    "expires_in": self.session_timeout
                }
                
                # Clean up pending auth
                if server_name in self.pending_auth:
                    del self.pending_auth[server_name]
                
                logger.info(f"Successfully authenticated with server {server_name} for phone {phone_number}")
                
                return {
                    "success": True,
                    "message": "Authentication successful",
                    "session_id": session_id
                }
            else:
                logger.error(f"Authentication failed with status {response.status_code}: {response.text}")
                return {
                    "success": False,
                    "error": f"Authentication failed: {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error during authentication with server {server_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def is_authenticated(self, server_name: str) -> bool:
        """Check if we're authenticated with a server"""
        if server_name not in self.authenticated_sessions:
            return False
        
        session_info = self.authenticated_sessions[server_name]
        
        # Check if session has expired
        if self._is_session_expired(session_info):
            # Clean up expired session
            del self.authenticated_sessions[server_name]
            logger.info(f"Session expired for server {server_name}")
            return False
            
        return session_info["status"] == "authenticated"

    def _is_session_expired(self, session_info: Dict[str, Any]) -> bool:
        """Check if a session has expired"""
        if "timestamp" not in session_info:
            return True  # No timestamp means expired
            
        import time
        current_time = time.time()
        session_time = session_info["timestamp"]
        
        return (current_time - session_time) > self.session_timeout

    def get_authentication_status(self, server_name: str) -> Dict[str, Any]:
        """Get authentication status for a server"""
        if server_name in self.authenticated_sessions:
            session_info = self.authenticated_sessions[server_name]
            
            # Check expiry
            if self._is_session_expired(session_info):
                del self.authenticated_sessions[server_name]
                return {"status": "expired", "message": "Session expired"}
                
            return session_info
        elif server_name in self.pending_auth:
            return self.pending_auth[server_name]
        else:
            return {"status": "not_authenticated"}

    def cleanup_expired_sessions(self):
        """Clean up all expired sessions"""
        expired_servers = []
        for server_name, session_info in self.authenticated_sessions.items():
            if self._is_session_expired(session_info):
                expired_servers.append(server_name)
        
        for server_name in expired_servers:
            del self.authenticated_sessions[server_name]
            logger.info(f"Cleaned up expired session for server {server_name}")
        
        return len(expired_servers)

    async def _call_http_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any], use_dummy_session: bool = False) -> Dict[str, Any]:
        """Call a tool on HTTP MCP server using proper MCP JSON-RPC protocol."""
        
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} is not configured")
        
        server_config = self.servers[server_name]
        mcp_url = server_config["url"]  # This should be http://localhost:8484/mcp/stream
        
        # Create JSON-RPC request for MCP protocol
        rpc_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Headers for MCP request - always include session ID
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add session ID if we're authenticated, otherwise use a dummy session to trigger auth flow
        session_id_to_use = None
        
        if not use_dummy_session and self.is_authenticated(server_name):
            # Use authenticated session ID
            auth_info = self.authenticated_sessions[server_name]
            session_id_to_use = auth_info["session_id"]
            headers["Mcp-Session-Id"] = session_id_to_use
        elif server_name in self.pending_auth:
            # Use existing pending session ID if available
            pending_session = self.pending_auth[server_name]
            session_id_to_use = pending_session["session_id"]
            headers["Mcp-Session-Id"] = session_id_to_use
        else:
            # Generate a new session ID and store it for future use
            session_id_to_use = f"mcp-session-{str(uuid.uuid4())}"
            headers["Mcp-Session-Id"] = session_id_to_use
            
            # Store this session as pending so we can reuse it
            self.pending_auth[server_name] = {
                "session_id": session_id_to_use,
                "phone_number": "unknown",  # We don't have phone number in this context
                "status": "pending_auth_redirect", 
                "timestamp": time.time()
            }
        
        try:
            logger.info(f"🌐 Making MCP JSON-RPC request to: {mcp_url}")
            logger.info(f"📋 Request payload: {json.dumps(rpc_request, indent=2)}")
            logger.info(f"📋 Request headers: {json.dumps(headers, indent=2)}")
            
            response = requests.post(mcp_url, json=rpc_request, headers=headers, timeout=30)
            
            logger.info(f"📦 Response status: {response.status_code}")
            logger.info(f"📦 Response headers: {dict(response.headers)}")
            logger.info(f"📦 Response text: {response.text}")
            
            # Handle authentication required responses
            if response.status_code == 400 and "Invalid session ID" in response.text:
                # Check if we already have a pending session, if not create one
                if server_name not in self.pending_auth:
                    # Generate session ID and login URL for authentication
                    session_id = f"mcp-session-{str(uuid.uuid4())}"
                    
                    # Store this session as pending authentication so we can reuse it
                    self.pending_auth[server_name] = {
                        "session_id": session_id,
                        "phone_number": "unknown",  # We don't have phone number in this context
                        "status": "pending_auth_redirect",
                        "timestamp": time.time()
                    }
                else:
                    # Use existing session ID
                    session_id = self.pending_auth[server_name]["session_id"]
                
                base_url = mcp_url.replace("/mcp/stream", "")
                login_url = f"{base_url}/wealth-mcp-login?token={session_id}"
                
                # Return authentication required response
                return {
                    "content": {
                        "status": "login_required",
                        "login_url": login_url,
                        "message": "Please complete authentication using the provided link",
                        "session_id": session_id
                    },
                    "success": True
                }
            
            response.raise_for_status()
            
            # Parse MCP JSON-RPC response
            rpc_response = response.json()
            logger.debug(f"📦 MCP response: {json.dumps(rpc_response, indent=2)}")
            
            # Check for JSON-RPC error
            if "error" in rpc_response:
                error_info = rpc_response["error"]
                return {
                    "content": f"MCP Error: {error_info.get('message', 'Unknown error')}",
                    "success": False,
                    "error": error_info
                }
            
            # Extract content from MCP response
            if "result" in rpc_response and "content" in rpc_response["result"]:
                content_list = rpc_response["result"]["content"]
                if content_list and len(content_list) > 0:
                    # Get the first content item (text)
                    content_item = content_list[0]
                    if content_item.get("type") == "text":
                        # Try to parse the text as JSON
                        text_content = content_item.get("text", "")
                        try:
                            parsed_content = json.loads(text_content)
                            return {
                                "content": parsed_content,
                                "success": True
                            }
                        except json.JSONDecodeError:
                            # If not JSON, return as text
                            return {
                                "content": text_content,
                                "success": True
                            }
            
            # Fallback: return the entire result
            return {
                "content": rpc_response.get("result", "No content returned"),
                "success": True
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout calling MCP tool {tool_name}")
            return {
                "content": f"Timeout calling tool {tool_name}",
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"❌ Error calling MCP tool {tool_name}: {str(e)}")
            return {
                "content": f"Error calling tool {tool_name}: {str(e)}",
                "success": False,
                "error": str(e)
            }

    def get_all_available_tools_sync(self) -> Dict[str, List[Dict]]:
        """Synchronous wrapper for getting all available tools."""
        return asyncio.run(self.get_all_available_tools())
    
    def get_tools_for_gemini(self) -> List[Dict]:
        """Convert MCP tools to Gemini-compatible format."""
        all_tools = self.get_all_available_tools_sync()
        gemini_tools = []
        
        for server_name, tools in all_tools.items():
            for tool in tools:
                # Convert MCP tool schema to Gemini function declaration format
                gemini_tool = {
                    "name": f"{server_name}_{tool['name']}",  # Prefix with server name
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
                gemini_tools.append(gemini_tool)
        
        return gemini_tools
    
    async def execute_tool_for_gemini(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call from Gemini and return the result."""
        try:
            # Parse server name from function name (format: server_name_tool_name)
            # We need to match against known server names to avoid incorrect splitting
            server_name = None
            tool_name = None
            
            logger.info(f"self.servers.keys: {self.servers.keys()}")
            # Try to match against known server names
            for known_server in self.servers.keys():
                prefix = f"{known_server}_"
                if function_name.startswith(prefix):
                    server_name = known_server
                    tool_name = function_name[len(prefix):]
                    break
            
            logger.info(f"function: {function_name}, args: {arguments}, server: {server_name}, tool: {tool_name}")
            # Fallback: if no match found, use first available server
            if server_name is None:
                if self.servers:
                    server_name = next(iter(self.servers.keys()))
                    tool_name = function_name
                else:
                    raise ValueError("No MCP servers available")
            
            result = await self.call_tool(server_name, tool_name, arguments)
            
            return {
                "success": True,
                "result": result.get("content") if isinstance(result, dict) else str(result),
                "server": server_name,
                "tool": tool_name
            }
        
        except Exception as e:
            logger.error(f"Error executing tool {function_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "server": server_name if 'server_name' in locals() else "unknown",
                "tool": tool_name if 'tool_name' in locals() else function_name
            }

    async def cleanup(self):
        """Clean up resources."""
        # Stop any running server processes
        for server_name, process in self.server_processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"Stopped server process for {server_name}")
            except:
                process.kill()
        
        await self.exit_stack.aclose()
    
    
_mcp_client = MCPClient()

def get_mcp_client() -> MCPClient:
    """Get the singleton MCP client instance"""
    return _mcp_client

