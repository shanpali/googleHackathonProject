from flask import Flask, request, jsonify, session, send_from_directory, abort

from flask import Flask, session, request, jsonify
from flask_cors import CORS
import requests
import os
import json
import logging
import asyncio
from config import Config
from gemini_service import get_gemini_service
from mcp_client import MCPClient, get_mcp_client
from function_implementations import (
    schedule_reminder,
    generate_financial_report,
    set_financial_goal,
    create_investment_alert
)

CHAT_HISTORY_STORE = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY
CORS(app, supports_credentials=True)

# Initialize Gemini service
gemini_service = get_gemini_service()

# Register function implementations
gemini_service.register_function("schedule_reminder", schedule_reminder)
gemini_service.register_function("generate_financial_report", generate_financial_report)
gemini_service.register_function("set_financial_goal", set_financial_goal)
gemini_service.register_function("create_investment_alert", create_investment_alert)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'test_data_dir')

DATA_ENDPOINTS = [
    'fetch_mf_transactions',
    'fetch_stock_transactions',
    'fetch_bank_transactions',
    'fetch_credit_report',
    'fetch_epf_details',
    'fetch_net_worth',
    # Add more as you add new JSON files (e.g., 'fetch_real_estate', 'fetch_gold', etc.)
]

@app.route('/login', methods=['POST'])
def login():
    phone = request.json.get('phone')
    session['phone'] = phone
    return jsonify({'success': True})

@app.route('/mcp-auth-callback', methods=['POST'])
def mcp_auth_callback():
    """Handle MCP authentication completion callback"""
    try:
        session_id = request.json.get('session_id')
        server_name = request.json.get('server_name', 'fi_mcp')  # default to fi_mcp
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        # Mark the session as authenticated
        mcp_client = get_mcp_client()
        result = mcp_client.mark_session_authenticated(server_name, session_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Authentication completed successfully',
                'session_id': session_id
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Authentication failed')
            }), 400
            
    except Exception as e:
        return jsonify({'error': f'Authentication callback failed: {str(e)}'}), 500

@app.route('/financial-data', methods=['GET'])
def financial_data():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    user_data = {}
    for endpoint in DATA_ENDPOINTS:
        try:
            user_dir = os.path.join(TEST_DATA_DIR, phone)
            file_path = os.path.join(user_dir, f"{endpoint}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    user_data[endpoint] = json.load(f)
            else:
                user_data[endpoint] = None
        except Exception as e:
            user_data[endpoint] = None

    return jsonify(user_data)

@app.route('/recommendations', methods=['GET'])
def recommendations():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    # Aggregate all data as above
    user_data = {}
    for endpoint in DATA_ENDPOINTS:
        try:
            user_dir = os.path.join(TEST_DATA_DIR, phone)
            file_path = os.path.join(user_dir, f"{endpoint}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    user_data[endpoint] = json.load(f)
            else:
                user_data[endpoint] = None
        except Exception:
            user_data[endpoint] = None

    # Use the new Gemini service for recommendations
    try:
        response = gemini_service.generate_recommendations(
            user_data=user_data,
            phone=phone,  # Pass phone for context loading
            focus_areas=["investment_optimization", "risk_assessment", "financial_planning"]
        )
        
        return jsonify({
            "recommendations": response.get('text', 'Unable to generate recommendations'),
            "function_calls": response.get('function_calls', []),
            "success": not response.get('error')
        })
    except Exception as e:
        return jsonify({'error': f'Failed to generate recommendations: {str(e)}'}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Optionally, fetch user data for context
    user_data = {}
    for endpoint in DATA_ENDPOINTS:
        try:
            user_dir = os.path.join(TEST_DATA_DIR, phone)
            file_path = os.path.join(user_dir, f"{endpoint}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    user_data[endpoint] = json.load(f)
            else:
                user_data[endpoint] = None
        except Exception:
            user_data[endpoint] = None

    # Maintain conversation history in session
    # Maintain conversation history in in-memory store
    user_id = session.get('phone') or request.remote_addr  # Use phone or IP as key
    if user_id not in CHAT_HISTORY_STORE:
        CHAT_HISTORY_STORE[user_id] = []
    chat_history = CHAT_HISTORY_STORE[user_id]
    
    # Add the new user message
    chat_history.append({'role': 'user', 'text': user_message})

    # Use the new Gemini service with enhanced context
    try:
        # Create enhanced user content with chat history
        history_context = ""
        if len(chat_history) > 1:  # If there's previous conversation
            recent_history = chat_history[-5:]  # Last 5 messages
            history_context = "Previous conversation:\n" + "\n".join([
                f"{msg['role'].capitalize()}: {msg['text']}" 
                for msg in recent_history[:-1]  # Exclude the current message
            ]) + "\n\nCurrent question: "
        
        full_user_content = history_context + user_message
        
        response = gemini_service.generate_content_with_user_context(
            user_content=full_user_content,
            phone=phone,  # Pass phone for context loading
            financial_data=user_data,
            include_tools=True,
            custom_tools=get_mcp_client().get_tools_for_gemini()
        )
        
        assistant_response = response.get('text', 'I apologize, but I encountered an error processing your request.')
        
        # Add Gemini's response to history
        chat_history.append({'role': 'assistant', 'text': assistant_response})
        CHAT_HISTORY_STORE[user_id] = chat_history
        
        return jsonify({
            "response": assistant_response,
            "function_calls": response.get('function_calls', []),
            "history": chat_history,
            "success": not response.get('error')
        })
        
    except Exception as e:
        return jsonify({'error': f'Chat processing failed: {str(e)}'}), 500

@app.route('/mcp/<filename>')
def serve_mock_data(filename):
    phone = request.args.get('phone')
    if not phone:
        return jsonify({'error': 'Missing phone parameter'}), 400

    user_dir = os.path.join(TEST_DATA_DIR, phone)
    file_path = os.path.join(user_dir, f"{filename}.json")
    if not os.path.exists(file_path):
        return jsonify({'error': 'Data not found'}), 404

    return send_from_directory(user_dir, f"{filename}.json")

@app.route('/call-function', methods=['POST'])
def execute_function_directly():
    #phone = session.get('phone')
    #if not phone:
    #    return jsonify({'error': 'Not logged in'}), 401

    function = request.json.get('function')
    args = request.json.get('args')
    if not function:
        return jsonify({'error': 'No function provided'}), 400
    logger.debug("got here: before mcp")
    try:
        mcp_client = get_mcp_client()  # Use singleton
        logger.debug("got here: got mcp client")
        result = asyncio.run(mcp_client.execute_tool_for_gemini(function_name=function, arguments=args))
        logger.debug(f"result: {result}")
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Function call failed: {str(e)}'}), 500

@app.route('/available-tools', methods=['GET'])
def available_tools():
    try:
        mcp_client = get_mcp_client()
        tools = mcp_client.get_tools_for_gemini()
        return jsonify({
            "tools": tools,
            "success": True
        })
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch available tools: {str(e)}",
            "success": False
        }), 500

if __name__ == '__main__':
    app.run(port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG) 

