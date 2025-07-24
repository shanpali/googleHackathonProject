"""
Tool registry for managing function implementations and tool definitions
"""

from typing import Dict, List, Callable, Any
import logging
from .tool_definitions import ToolDefinitions

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Manages tool definitions and their implementations
    """
    
    def __init__(self):
        """Initialize the tool registry"""
        self.function_registry: Dict[str, Callable] = {}
        self.tool_definitions: Dict[str, Dict] = {}
        self._setup_default_tools()
    
    def _setup_default_tools(self):
        """Setup default tool definitions"""
        default_tools = ToolDefinitions.get_all_default_tools()
        for tool in default_tools:
            self.tool_definitions[tool["name"]] = tool
        
        logger.info(f"Loaded {len(default_tools)} default tool definitions")
    
    def register_function(self, name: str, function: Callable, tool_definition: Dict = None):
        """
        Register a function implementation with optional tool definition
        
        Args:
            name: Function name
            function: Function implementation
            tool_definition: Optional tool definition (if not using default)
        """
        self.function_registry[name] = function
        
        if tool_definition:
            self.tool_definitions[name] = tool_definition
        
        logger.info(f"Registered function: {name}")
    
    def register_custom_tool(self, tool_definition: Dict, implementation: Callable):
        """
        Register a custom tool with both definition and implementation
        
        Args:
            tool_definition: Tool schema definition
            implementation: Function implementation
        """
        tool_name = tool_definition.get("name")
        if not tool_name:
            raise ValueError("Tool definition must have a 'name' field")
        
        self.tool_definitions[tool_name] = tool_definition
        self.function_registry[tool_name] = implementation
        
        logger.info(f"Registered custom tool: {tool_name}")
    
    def get_function(self, name: str) -> Callable:
        """Get a registered function by name"""
        return self.function_registry.get(name)
    
    def get_tool_definition(self, name: str) -> Dict:
        """Get a tool definition by name"""
        return self.tool_definitions.get(name)
    
    def get_all_tool_definitions(self, include_custom: bool = True) -> List[Dict]:
        """
        Get all tool definitions
        
        Args:
            include_custom: Whether to include custom tools or just defaults
        """
        if include_custom:
            return list(self.tool_definitions.values())
        else:
            return ToolDefinitions.get_all_default_tools()
    
    def get_registered_functions(self) -> Dict[str, Callable]:
        """Get all registered function implementations"""
        return self.function_registry.copy()
    
    def execute_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a registered function
        
        Args:
            function_name: Name of the function to execute
            **kwargs: Function arguments
            
        Returns:
            Dict with execution result
        """
        if function_name not in self.function_registry:
            return {
                "success": False,
                "error": f"Function '{function_name}' not registered",
                "function": function_name
            }
        
        try:
            result = self.function_registry[function_name](**kwargs)
            return {
                "success": True,
                "result": result,
                "function": function_name
            }
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "function": function_name
            }
    
    def has_function(self, name: str) -> bool:
        """Check if a function is registered"""
        return name in self.function_registry
    
    def has_tool_definition(self, name: str) -> bool:
        """Check if a tool definition exists"""
        return name in self.tool_definitions
    
    def unregister_function(self, name: str):
        """Unregister a function and its tool definition"""
        if name in self.function_registry:
            del self.function_registry[name]
        if name in self.tool_definitions:
            del self.tool_definitions[name]
        logger.info(f"Unregistered function: {name}")

# Singleton instance
_tool_registry = ToolRegistry()

def get_tool_registry() -> ToolRegistry:
    """Get the singleton tool registry instance"""
    return _tool_registry
