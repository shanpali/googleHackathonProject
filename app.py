from flask import Flask, jsonify, request
import os
import fi_money_mcp
import gemini
import json
from i18n import get_localized_error, ErrorCodes
from prompt_service import prompt_service

app = Flask(__name__)

# Load MCP servers at startup
with open('mcp_servers.json', 'r') as f:
    mcp_servers = json.load(f)

# Prompts are now loaded by prompt_service

@app.route('/api/user/recommendations', methods=['GET'])
def get_recommendations():
    # In a real application, the user token would be passed in the request
    # headers or body.
    user_token = 'mock-user-token'

    try:
        financial_data = fi_money_mcp.get_financial_data(user_token)
        # Use the default financial_analysis prompt with enhanced variables
        prompt_variables = {
            'financial_data': financial_data,
            'focus_area': 'general financial health'
        }
        prompt_template = prompt_service.render_prompt('financial_analysis', prompt_variables)
        recommendations = gemini.get_gemini_recommendations(financial_data, prompt_template)
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        print(f"Error: {e}")
        error_message = get_localized_error(ErrorCodes.SERVER_FINANCIAL_DATA_ERROR)
        return jsonify({'error': error_message}), 500

@app.route('/api/mcp/prompt', methods=['POST'])
def mcp_prompt():
    data = request.get_json()
    prompt_id = data.get('prompt_id')
    user_request = data.get('user_request', '')  # Natural language request from user
    
    # Extract user token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        error_message = get_localized_error(ErrorCodes.AUTH_MISSING_BEARER_TOKEN)
        return jsonify({'error': error_message}), 401
    
    user_token = auth_header.split(' ')[1]  # Extract token after "Bearer "

    if not prompt_id:
        error_message = get_localized_error(ErrorCodes.VALIDATION_MISSING_REQUIRED_FIELDS)
        return jsonify({'error': 'prompt_id is required'}), 400

    # Validate prompt exists
    prompt_info = prompt_service.get_prompt_info(prompt_id)
    if not prompt_info:
        error_message = get_localized_error(ErrorCodes.VALIDATION_INVALID_PROMPT)
        return jsonify({'error': error_message}), 404

    try:
        # Let the LLM decide what data/tools it needs based on the prompt and user request
        available_tools = _get_available_tools_description()
        
        # Build context for LLM to make decisions
        decision_context = {
            'user_request': user_request,
            'available_tools': available_tools,
            'user_token': user_token
        }
        
        # Get the LLM to analyze what tools/data it needs
        required_data = _determine_required_data(prompt_id, decision_context)
        
        # Extract prompt variables from request data (optional)
        prompt_variables = data.get('variables', {})
        
        # Add the dynamically gathered data
        prompt_variables.update(required_data)
        
        # Render the prompt with variables and user's preferred language
        rendered_prompt = prompt_service.render_prompt(prompt_id, prompt_variables)
        
        # Get recommendations from Gemini
        recommendations = gemini.get_gemini_recommendations(required_data.get('financial_data', {}), rendered_prompt)

        return jsonify({
            'recommendations': recommendations,
            'prompt_id': prompt_id,
            'tools_used': list(required_data.keys()),
            'variables_used': prompt_variables
        })
    except ValueError as e:
        # Handle prompt service validation errors
        print(f"Validation Error: {e}")
        error_message = get_localized_error(ErrorCodes.VALIDATION_INVALID_PROMPT)
        return jsonify({'error': f"{error_message}: {str(e)}"}), 400
    except Exception as e:
        print(f"Error: {e}")
        error_message = get_localized_error(ErrorCodes.SERVER_PROCESSING_ERROR)
        return jsonify({'error': error_message}), 500


def _get_available_tools_description():
    """Get description of all available MCP tools/data sources for LLM decision making."""
    return {
        'financial_data': {
            'description': 'User financial data including income, expenses, debts, assets, and spending patterns',
            'function': 'fi_money_mcp.get_financial_data',
            'required_params': ['user_token'],
            'use_cases': ['financial analysis', 'budget planning', 'investment advice', 'debt management']
        }
    }


def _determine_required_data(prompt_id, context):
    """
    Use LLM to intelligently determine what data/tools are needed based on:
    - The prompt type
    - User's natural language request
    - Available tools
    """
    user_request = context.get('user_request', '')
    user_token = context['user_token']
    available_tools = context['available_tools']
    
    # Get prompt info to understand what it typically needs
    prompt_info = prompt_service.get_prompt_info(prompt_id)
    
    # Create a decision prompt for the LLM
    decision_prompt = f"""
You are an intelligent agent that determines what data sources are needed to fulfill a user request.

USER REQUEST: "{user_request}"
PROMPT TYPE: {prompt_id} - {prompt_info.get('description', '')}
PROMPT CATEGORY: {prompt_info.get('category', '')}

AVAILABLE TOOLS:
{json.dumps(available_tools, indent=2)}

Based on the user request and prompt type, determine which tools/data sources are needed.
Return a JSON object with the tools to use and any additional context.

Example response:
{{
    "tools_needed": ["financial_data"],
    "reasoning": "Financial analysis requires user's financial data",
    "additional_context": "Focus on budgeting based on user request"
}}

Response (JSON only):"""
    
    try:
        # Use Gemini to make the decision
        decision_response = gemini.get_gemini_recommendations({}, decision_prompt)
        
        # Parse the LLM's decision (in a real system, you'd have better JSON parsing)
        import re
        json_match = re.search(r'\{.*\}', decision_response, re.DOTALL)
        if json_match:
            decision = json.loads(json_match.group())
        else:
            # Fallback decision
            decision = {"tools_needed": ["financial_data"], "reasoning": "Default fallback"}
        
        print(f"LLM Decision: {decision}")
        
        # Execute the tools the LLM determined are needed
        required_data = {}
        
        for tool_name in decision.get('tools_needed', []):
            if tool_name == 'financial_data' and available_tools[tool_name]:
                required_data['financial_data'] = fi_money_mcp.get_financial_data(user_token)
            # Add more tool implementations here as they become available
            # elif tool_name == 'market_data':
            #     required_data['market_data'] = market_mcp.get_market_data(symbols)
        
        # Add reasoning to help with prompt rendering
        required_data['llm_reasoning'] = decision.get('reasoning', '')
        required_data['additional_context'] = decision.get('additional_context', '')
        
        return required_data
        
    except Exception as e:
        print(f"Error in LLM decision making: {e}")
        # Fallback to getting financial data for financial prompts
        fallback_data = {}
        if prompt_info.get('category') in ['financial_planning', 'investments', 'debt_management', 'budgeting']:
            fallback_data['financial_data'] = fi_money_mcp.get_financial_data(user_token)
        return fallback_data


@app.route('/api/intelligent-advice', methods=['POST'])
def intelligent_advice():
    """
    Intelligent endpoint where user just describes what they want,
    and the LLM figures out what tools/data to use and how to respond.
    """
    data = request.get_json()
    user_request = data.get('user_request', '')
    
    # Extract user token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        error_message = get_localized_error(ErrorCodes.AUTH_MISSING_BEARER_TOKEN)
        return jsonify({'error': error_message}), 401
    
    user_token = auth_header.split(' ')[1]
    
    if not user_request:
        return jsonify({'error': 'user_request is required'}), 400
    
    try:
        # Step 1: LLM determines what type of advice this is and what tools are needed
        available_tools = _get_available_tools_description()
        
        analysis_prompt = f"""
You are a financial advisor AI. A user has made this request: "{user_request}"

Available tools and data sources:
{json.dumps(available_tools, indent=2)}

Determine:
1. What type of financial advice this is
2. What data/tools you need
3. What specific prompt template would be best

Respond with JSON:
{{
    "advice_type": "investment|budgeting|debt_management|general_financial",
    "suggested_prompt": "investment_suggestions|financial_analysis|debt_reduction_plan|budget_optimization",
    "tools_needed": ["financial_data"],
    "reasoning": "explanation of your decision",
    "focus_areas": ["specific areas to focus on"]
}}
"""
        
        # Get LLM analysis
        analysis_response = gemini.get_gemini_recommendations({}, analysis_prompt)
        
        # Parse the analysis (simplified JSON extraction)
        import re
        json_match = re.search(r'\{.*\}', analysis_response, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
        else:
            # Fallback
            analysis = {
                "suggested_prompt": "financial_analysis",
                "tools_needed": ["financial_data"],
                "reasoning": "General financial analysis"
            }
        
        # Step 2: Gather the required data
        required_data = {}
        for tool_name in analysis.get('tools_needed', []):
            if tool_name == 'financial_data':
                required_data['financial_data'] = fi_money_mcp.get_financial_data(user_token)
        
        # Step 3: Use the suggested prompt with custom variables
        prompt_id = analysis.get('suggested_prompt', 'financial_analysis')
        prompt_variables = {
            'financial_data': required_data.get('financial_data', {}),
            'focus_area': ', '.join(analysis.get('focus_areas', ['general financial health'])),
            'user_specific_request': user_request
        }
        
        # Render the prompt
        rendered_prompt = prompt_service.render_prompt(prompt_id, prompt_variables)
        
        # Add user's specific request context
        enhanced_prompt = rendered_prompt + f"\n\nUser's specific request: {user_request}\nFocus particularly on addressing this request."
        
        # Step 4: Get the final recommendation
        recommendations = gemini.get_gemini_recommendations(required_data.get('financial_data', {}), enhanced_prompt)
        
        return jsonify({
            'recommendations': recommendations,
            'analysis': analysis,
            'tools_used': list(required_data.keys()),
            'user_request': user_request
        })
        
    except Exception as e:
        print(f"Error in intelligent advice: {e}")
        error_message = get_localized_error(ErrorCodes.SERVER_PROCESSING_ERROR)
        return jsonify({'error': error_message}), 500


@app.route('/api/prompts', methods=['GET'])
def list_prompts():
    """List all available prompts with their metadata."""
    try:
        prompts_info = {}
        for prompt_id, prompt_data in prompt_service.prompts.items():
            if isinstance(prompt_data, dict):
                prompts_info[prompt_id] = {
                    'description': prompt_data.get('description', ''),
                    'category': prompt_data.get('category', ''),
                    'variables': prompt_data.get('variables', {}),
                    'max_tokens': prompt_data.get('max_tokens', 1000)
                }
        
        return jsonify({
            'prompts': prompts_info,
            'categories': prompt_service.get_prompt_categories()
        })
    except Exception as e:
        print(f"Error: {e}")
        error_message = get_localized_error(ErrorCodes.SERVER_PROCESSING_ERROR)
        return jsonify({'error': error_message}), 500


@app.route('/api/prompts/<prompt_id>/schema', methods=['GET'])
def get_prompt_schema(prompt_id):
    """Get the JSON schema for a specific prompt's variables."""
    try:
        schema = prompt_service.get_prompt_schema(prompt_id)
        return jsonify(schema)
    except ValueError as e:
        error_message = get_localized_error(ErrorCodes.VALIDATION_INVALID_PROMPT)
        return jsonify({'error': f"{error_message}: {str(e)}"}), 404
    except Exception as e:
        print(f"Error: {e}")
        error_message = get_localized_error(ErrorCodes.SERVER_PROCESSING_ERROR)
        return jsonify({'error': error_message}), 500


@app.route('/api/prompts/categories/<category>', methods=['GET'])
def get_prompts_by_category(category):
    """Get all prompts in a specific category."""
    try:
        prompts_in_category = prompt_service.get_prompts_by_category(category)
        if not prompts_in_category:
            error_message = get_localized_error(ErrorCodes.VALIDATION_INVALID_PROMPT)
            return jsonify({'error': f"No prompts found in category: {category}"}), 404
        
        return jsonify({
            'category': category,
            'prompts': prompts_in_category
        })
    except Exception as e:
        print(f"Error: {e}")
        error_message = get_localized_error(ErrorCodes.SERVER_PROCESSING_ERROR)
        return jsonify({'error': error_message}), 500


if __name__ == '__main__':
    app.run(debug=True, port=3000)
