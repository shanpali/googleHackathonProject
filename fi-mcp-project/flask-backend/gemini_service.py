from google import genai
from google.genai import types
from typing import Dict, List, Optional, Any, Callable
import logging
from config import Config
from user_context_manager import get_user_context_manager
from tools import get_tool_registry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    """
    Modular Gemini AI service with function tools support
    """
    
    def __init__(self):
        """Initialize the Gemini service"""
        Config.validate_config()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.context_manager = get_user_context_manager()
        self.tool_registry = get_tool_registry()
    
    def register_function(self, name: str, function: Callable, tool_definition: Dict = None):
        """Register a custom function for tool calling"""
        self.tool_registry.register_function(name, function, tool_definition)
    
    def register_custom_tool(self, tool_definition: Dict, implementation: Callable):
        """Register a custom tool with both definition and implementation"""
        self.tool_registry.register_custom_tool(tool_definition, implementation)
    
    def _execute_function_call(self, function_call) -> Dict[str, Any]:
        """Execute a function call and return the result"""
        function_name = function_call.name
        function_args = dict(function_call.args)
        
        if self.tool_registry.has_function(function_name):
            return self.tool_registry.execute_function(function_name, **function_args)
        else:
            # For demo purposes, return a mock result
            logger.info(f"Mock execution of {function_name} with args: {function_args}")
            return {
                "success": True, 
                "result": f"Mock execution of {function_name} completed successfully",
                "function": function_name,
                "args": function_args
            }
    
    def generate_content_with_user_context(
        self,
        user_content: str,
        phone: str = None,
        financial_data: Optional[Dict] = None,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        include_tools: bool = True,
        custom_tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate content with full user context including existing reminders, goals, and alerts
        
        Args:
            user_content (str): The user's message or query
            phone (str): User's phone number for context loading
            financial_data (Dict, optional): User's financial data
            system_instruction (str, optional): System instruction for the AI
            model (str, optional): Model to use (defaults to config model)
            include_tools (bool): Whether to include function tools
            custom_tools (List[Dict], optional): Additional custom tool definitions
            
        Returns:
            Dict containing the response and any function calls
        """
        # Enhance the user content with existing user context
        enhanced_user_content = self.context_manager.get_contextual_prompt_enhancement(
            base_prompt=user_content,
            phone=phone,
            financial_data=financial_data
        )
        
        # Call the main generate_content method with enhanced context
        return self.generate_content(
            user_content=enhanced_user_content,
            system_instruction=system_instruction,
            model=model,
            include_tools=include_tools,
            custom_tools=custom_tools,
            user_context=None  # Context is already embedded in the enhanced content
        )

    def generate_content(
        self,
        user_content: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        include_tools: bool = True,
        custom_tools: Optional[List[Dict]] = None,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate content using Gemini AI with optional tools and system instructions
        
        Args:
            user_content (str): The user's message or query
            system_instruction (str, optional): System instruction for the AI
            model (str, optional): Model to use (defaults to config model)
            include_tools (bool): Whether to include function tools
            custom_tools (List[Dict], optional): Additional custom tool definitions
            user_context (Dict, optional): Additional context (e.g., user financial data)
            
        Returns:
            Dict containing the response and any function calls
        """
        try:
            # Use default system instruction if none provided
            if system_instruction is None:
                system_instruction = Config.DEFAULT_SYSTEM_INSTRUCTION
            
            # Use default model if none provided
            if model is None:
                model = Config.GEMINI_MODEL
            
            # Prepare the content with context if provided
            if user_context:
                enhanced_content = f"User Context: {user_context}\n\nUser Query: {user_content}"
            else:
                enhanced_content = user_content
            
            # Setup configuration
            config_params = {
                "system_instruction": system_instruction
            }
            
            # Add tools if requested
            if include_tools:
                all_functions = self.tool_registry.get_all_tool_definitions().copy()
                if custom_tools:
                    all_functions.extend(custom_tools)
                
                if all_functions:
                    tools = types.Tool(function_declarations=all_functions)
                    config_params["tools"] = [tools]
            
            config = types.GenerateContentConfig(**config_params)
            
            # Generate content
            response = self.client.models.generate_content(
                model=model,
                contents=enhanced_content,
                config=config,
            )
            
            # Process response
            result = {
                "text": response.text,
                "function_calls": [],
                "raw_response": response
            }
            
            # Handle function calls if present
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            function_result = self._execute_function_call(part.function_call)
                            result["function_calls"].append(function_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return {
                "error": str(e),
                "text": None,
                "function_calls": []
            }
    
    def generate_recommendations(
        self,
        user_data: Dict[str, Any],
        phone: str = None,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized financial recommendations based on user data
        
        Args:
            user_data (Dict): User's financial data
            phone (str): User's phone number for context
            focus_areas (List[str], optional): Specific areas to focus on
            
        Returns:
            Dict containing recommendations
        """
        focus_text = ""
        if focus_areas:
            focus_text = f"Focus particularly on: {', '.join(focus_areas)}. "
        
        prompt = f"""
        {focus_text}Based on the user's financial data and existing goals/reminders/alerts, provide personalized recommendations:
        
        1. Immediate action items (next 30 days)
        2. Medium-term strategies (3-12 months)  
        3. Long-term planning (1+ years)
        4. Risk assessment and mitigation
        5. Investment optimization opportunities
        
        Please consider existing goals and reminders to avoid duplicates and provide complementary advice.
        Be specific and actionable in your recommendations.
        """
        
        return self.generate_content_with_user_context(
            user_content=prompt,
            phone=phone,
            financial_data=user_data,
            model=Config.GEMINI_FLASH_MODEL  # Use faster model for recommendations
        )

# Singleton instance
gemini_service = GeminiService()

def get_gemini_service() -> GeminiService:
    """Get the singleton Gemini service instance"""
    return gemini_service
