from flask import Flask, request, jsonify, session, send_from_directory, abort
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app, supports_credentials=True)

# Removed: FI_MCP_URL and all Go server related code
GEMINI_API_URL = 'https://gemini.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyCI43NmQ0bhy_IxU1Y3vv1pLc8KPUvXHKk'

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
        except Exception as e:
            user_data[endpoint] = None

    # Call Gemini API
    gemini_payload = {
        "contents": [{"parts": [{"text": f"Give recommendations for: {user_data}"}]}]
    }
    gemini_resp = requests.post(GEMINI_API_URL, json=gemini_payload)
    return jsonify(gemini_resp.json())

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
        except Exception as e:
            user_data[endpoint] = None

    # Maintain conversation history in session
    if 'chat_history' not in session:
        session['chat_history'] = []
    chat_history = session['chat_history']
    # Add the new user message
    chat_history.append({'role': 'user', 'text': user_message})

    # Compose prompt for Gemini with context retention and prefix
    prefix = "Act as a financial advisor or wealth manager while looking into given data."
    history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['text']}" for msg in chat_history])
    prompt = f"{prefix}\nUser financial data: {user_data}\n{history_text}"
    gemini_payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    gemini_resp = requests.post(GEMINI_API_URL, json=gemini_payload)
    # Add Gemini's response to history
    gemini_text = gemini_resp.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', str(gemini_resp.json()))
    chat_history.append({'role': 'assistant', 'text': gemini_text})
    session['chat_history'] = chat_history
    return jsonify({"response": gemini_text, "history": chat_history})

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

if __name__ == '__main__':
    app.run(port=5000, debug=True) 