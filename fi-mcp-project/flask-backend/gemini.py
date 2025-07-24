"""
Simple example of using the modular Gemini service
This file demonstrates the clean, modular Gemini integration
"""

from gemini_service import get_gemini_service
from tools import get_tool_registry
import function_implementations  # This auto-registers the functions
import os

def create_sample_data_if_needed():
    """Create sample data files if they don't exist"""
    if not os.path.exists("user_reminders.json"):
        print("📋 Creating sample data files...")
        try:
            from create_sample_data import create_sample_data
            create_sample_data()
        except ImportError:
            print("⚠️  Could not create sample data. Please run: python3 create_sample_data.py")

def main():
    # Create sample data if needed
    create_sample_data_if_needed()
    
    # Get the Gemini service instance (functions are auto-registered)
    service = get_gemini_service()
    
    # Get tool registry to check what's registered
    tool_registry = get_tool_registry()
    print(f"🔧 Registered tools: {list(tool_registry.get_registered_functions().keys())}")
    
    print("=== Modular Gemini AI Financial Assistant Demo ===")
    print("🤖 Loading user context and financial data...")
    print()
    
    # Example 1: Simple query without tools
    print("=== Example 1: Simple Financial Advice ===")
    response = service.generate_content(
        user_content="What are the key principles of building wealth?",
        include_tools=False
    )
    print(f"Response: {response['text']}")
    print()
    
    # Example 2: Context-Aware Query with existing user data
    print("=== Example 2: Context-Aware Query ===")
    sample_user_data = {
        "fetch_net_worth": {
            "total_assets": 125000,
            "total_liabilities": 45000
        },
        "fetch_bank_transactions": {
            "transactions": [{"amount": -50, "description": "Grocery Store"}] * 15
        },
        "fetch_mf_transactions": {
            "holdings": [{"symbol": "VTSAX", "value": 25000}] * 8
        },
        "fetch_credit_report": {
            "credit_score": 750
        }
    }
    
    response = service.generate_content_with_user_context(
        user_content="I want to set a new savings goal. What should I focus on?",
        phone="1234567890",
        financial_data=sample_user_data
    )
    print(f"Context-aware response: {response['text']}")
    print()
    
    # Example 3: Function Tool Usage
    print("=== Example 3: Function Tool Usage ===")
    response = service.generate_content_with_user_context(
        user_content="Help me set a goal to save for a vacation. I want to save $5,000 by next summer.",
        phone="1234567890",
        financial_data=sample_user_data,
        include_tools=True
    )
    print(f"Response: {response['text']}")
    if response['function_calls']:
        for call in response['function_calls']:
            print(f"Function executed: {call}")
    print()
    
    # Example 4: Adding a custom tool
    print("=== Example 4: Custom Tool Registration ===")
    
    # Define a custom tool
    def create_budget_category(category_name: str, monthly_limit: float):
        return {
            "success": True,
            "category": category_name,
            "limit": monthly_limit,
            "message": f"Budget category '{category_name}' created with ${monthly_limit} monthly limit"
        }
    
    custom_tool_def = {
        "name": "create_budget_category",
        "description": "Creates a new budget category with spending limits",
        "parameters": {
            "type": "object",
            "properties": {
                "category_name": {
                    "type": "string",
                    "description": "Name of the budget category"
                },
                "monthly_limit": {
                    "type": "number", 
                    "description": "Monthly spending limit for this category"
                }
            },
            "required": ["category_name", "monthly_limit"]
        }
    }
    
    # Register the custom tool
    service.register_custom_tool(custom_tool_def, create_budget_category)
    
    response = service.generate_content(
        user_content="Help me create a budget category for dining out with a $300 monthly limit",
        include_tools=True
    )
    print(f"Custom tool response: {response['text']}")
    if response['function_calls']:
        for call in response['function_calls']:
            print(f"Custom function executed: {call}")

if __name__ == "__main__":
    main()
