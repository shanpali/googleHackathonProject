#!/usr/bin/env python3
"""
Demonstration of the enhanced prompt system with variables and internationalization.
Shows practical examples of how the new features work.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(__file__))

from prompt_service import prompt_service

def demonstrate_enhanced_prompts():
    print("🚀 ENHANCED PROMPT SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Example 1: Basic prompt rendering
    print("\n📝 1. BASIC PROMPT WITH VARIABLES")
    print("-" * 40)
    
    variables = {
        'financial_data': {
            'income': 5000,
            'expenses': 3500,
            'debts': 15000,
            'savings': 2000
        },
        'focus_area': 'debt reduction'
    }
    
    try:
        rendered = prompt_service.render_prompt('financial_analysis', variables, 'en')
        print(f"English prompt:")
        print(f"  {rendered[:200]}...")
        
        rendered_es = prompt_service.render_prompt('financial_analysis', variables, 'es')
        print(f"\nSpanish prompt:")
        print(f"  {rendered_es[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Investment suggestions with risk tolerance
    print("\n📈 2. INVESTMENT SUGGESTIONS WITH CUSTOM VARIABLES")
    print("-" * 50)
    
    investment_vars = {
        'financial_data': {
            'income': 7000,
            'savings': 50000,
            'current_investments': 25000
        },
        'risk_tolerance': 'aggressive',
        'timeline': '10 years'
    }
    
    try:
        rendered = prompt_service.render_prompt('investment_suggestions', investment_vars, 'fr')
        print(f"French investment prompt:")
        print(f"  {rendered[:250]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Schema information
    print("\n📋 3. PROMPT SCHEMA AND VALIDATION")
    print("-" * 40)
    
    try:
        schema = prompt_service.get_prompt_schema('debt_reduction_plan')
        print("Debt reduction plan variables schema:")
        for var_name, var_info in schema['properties'].items():
            required = "✓" if var_name in schema['required'] else "○"
            default = f" (default: {var_info.get('default', 'none')})" if 'default' in var_info else ""
            print(f"  {required} {var_name}: {var_info.get('description', '')}{default}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Categories
    print("\n📂 4. PROMPT CATEGORIES")
    print("-" * 25)
    
    categories = prompt_service.get_prompt_categories()
    print(f"Available categories: {', '.join(categories)}")
    
    for category in categories:
        prompts_in_cat = prompt_service.get_prompts_by_category(category)
        print(f"\n{category.upper()}:")
        for prompt_id, prompt_info in prompts_in_cat.items():
            print(f"  • {prompt_id}: {prompt_info.get('description', 'No description')}")

def show_api_examples():
    print("\n\n🌐 API USAGE EXAMPLES")
    print("=" * 60)
    
    print("\n1. BASIC PROMPT REQUEST (auto-detects language from Accept-Language header):")
    print("""
curl -X POST http://localhost:3000/api/mcp/prompt \\
  -H "Content-Type: application/json" \\
  -H "Accept-Language: es" \\
  -H "Authorization: Bearer your-token" \\
  -d '{
    "mcp_server_id": "fi_money",
    "prompt_id": "financial_analysis",
    "variables": {
      "focus_area": "savings optimization"
    }
  }'
""")
    
    print("\n2. INVESTMENT SUGGESTIONS WITH CUSTOM VARIABLES:")
    print("""
curl -X POST http://localhost:3000/api/mcp/prompt \\
  -H "Content-Type: application/json" \\
  -H "Accept-Language: fr" \\
  -H "Authorization: Bearer your-token" \\
  -d '{
    "mcp_server_id": "fi_money",
    "prompt_id": "investment_suggestions",
    "variables": {
      "risk_tolerance": "conservative",
      "timeline": "20 years"
    }
  }'
""")
    
    print("\n3. GET PROMPT SCHEMA:")
    print("""
curl -X GET http://localhost:3000/api/prompts/debt_reduction_plan/schema
""")
    
    print("\n4. LIST ALL PROMPTS:")
    print("""
curl -X GET http://localhost:3000/api/prompts
""")

def show_benefits():
    print("\n\n✨ BENEFITS OF THE ENHANCED SYSTEM")
    print("=" * 60)
    
    benefits = [
        "🌍 **Automatic Language Detection**: Responses in user's preferred language",
        "🔧 **Flexible Variables**: Customizable prompts with defaults and validation", 
        "📝 **Type Safety**: Schema validation for variables with clear error messages",
        "📂 **Organization**: Prompts organized by categories for better management",
        "🎯 **Targeted Responses**: Variables like risk_tolerance, timeline, focus_area",
        "🔄 **Extensible**: Easy to add new prompts, variables, and languages",
        "📚 **Self-Documenting**: Schema endpoint provides API documentation",
        "🛡️ **Robust**: Graceful fallbacks and comprehensive error handling",
        "🚀 **LLM Optimized**: Max tokens, instructions, and prompt engineering best practices",
        "🌟 **User Experience**: Personalized responses based on user preferences"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")

if __name__ == "__main__":
    demonstrate_enhanced_prompts()
    show_api_examples()
    show_benefits()
    
    print("\n\n🎉 The enhanced prompt system is ready!")
    print("Start the Flask app and try the API endpoints above.")
