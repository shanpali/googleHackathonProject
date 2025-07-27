from flask import Flask, request, jsonify, session, send_from_directory, abort
from flask_cors import CORS
import requests
import os
import json
import logging
from dotenv import load_dotenv
import re
from datetime import datetime, timedelta, timezone

# Import Firebase modules
from firebase_config import initialize_firebase, get_firestore_db, COLLECTIONS
from firebase_models import (
    FirebaseUserInsights, FirebaseUserGoals, FirebaseUserChatHistory,
    FirebaseUserHealthScore, FirebaseUserGoalInsights, FirebaseUserProfile,
    FirebaseUserNews, FirebaseUserCashTransaction
)

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize Firebase
initialize_firebase()

# IST is UTC+5:30
def now_ist():
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key_here')
CORS(app, supports_credentials=True)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-pro')
GEMINI_FLASH_MODEL = os.environ.get('GEMINI_FLASH_MODEL', 'gemini-2.5-flash')
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}'

DEFAULT_SYSTEM_INSTRUCTION = os.environ.get('DEFAULT_SYSTEM_INSTRUCTION',
    "You are a professional financial advisor and wealth manager. Provide accurate, helpful, and personalized financial advice based on the user's data and questions. Always prioritize the user's financial well-being and provide actionable insights.")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEST_DATA_DIR = os.path.join(BASE_DIR, 'test_data_dir')

DATA_ENDPOINTS = [
    'fetch_mf_transactions',
    'fetch_stock_transactions',
    'fetch_bank_transactions',
    'fetch_credit_report',
    'fetch_epf_details',
    'fetch_net_worth',
    'fetch_nominee_details',
    # Add more as you add new JSON files (e.g., 'fetch_real_estate', 'fetch_gold', etc.)
]

@app.route('/login', methods=['POST'])
def login():
    phone = request.json.get('phone')
    session['phone'] = phone
    return jsonify({'success': True})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
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

    # Add cash assets to net worth
    cash_assets = get_user_cash_assets(phone)
    total_cash = sum(a['amount'] for a in cash_assets)
    # Patch net worth in response
    try:
        networth = user_data.get('fetch_net_worth', {}).get('netWorthResponse', {})
        if networth and 'totalNetWorthValue' in networth:
            orig = float(networth['totalNetWorthValue']['units'])
            networth['totalNetWorthValue']['units'] = orig + total_cash
            # Optionally, add a cash asset entry to assetValues
            if total_cash > 0:
                networth['assetValues'].append({
                    'netWorthAttribute': 'ASSET_TYPE_CASH',
                    'value': {'currencyCode': 'INR', 'units': str(total_cash)}
                })
    except Exception:
        pass
    user_data['cash_assets'] = cash_assets
    return jsonify(user_data)

@app.route('/recommendations', methods=['GET'])
def recommendations():
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

    prompt = (
        "Act as a top-tier Indian financial advisor and tax expert. "
        "Given the user's financial data below, generate a JSON array of 3-5 proactive, actionable recommendations. "
        "Each recommendation should have: title, priority (High/Medium/Low), description, action (short CTA), save (potential savings or benefit, if any), and a suggested icon (choose from: 'tax', 'portfolio', 'spending', 'opportunity', 'alert'). "
        "Focus on Indian tax-saving, investment optimization, risk, and wealth-building opportunities. "
        "Respond ONLY with a JSON array, no extra text.\n"
        f"User financial data: {user_data}"
    )
    gemini_payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        gemini_resp = requests.post(GEMINI_API_URL, json=gemini_payload)
        if gemini_resp.status_code != 200:
            logging.error(f"Gemini API error: {gemini_resp.status_code} {gemini_resp.text}")
            return jsonify({"error": "Gemini API error", "details": gemini_resp.text}), 500
        candidates = gemini_resp.json().get('candidates', [])
        if candidates:
            text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            try:
                # Remove Markdown code block markers if present
                cleaned_text = text.strip()
                if cleaned_text.startswith('```'):
                    cleaned_text = re.sub(r'^```[a-zA-Z]*\s*', '', cleaned_text)
                    cleaned_text = re.sub(r'```$', '', cleaned_text)
                    cleaned_text = cleaned_text.strip()
                recommendations = json.loads(cleaned_text)
                return jsonify({"recommendations": recommendations})
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse Gemini response as JSON: {e}")
                return jsonify({"error": "Failed to parse AI response"}), 500
        else:
            return jsonify({"error": "No response from Gemini API"}), 500
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to get recommendations"}), 500

# Helper function to get last_updated timestamp from Firebase records
def get_firebase_last_updated(collection_name, phone):
    """Get the last_updated timestamp from a Firebase document"""
    try:
        db = get_firestore_db()
        if db:
            doc_ref = db.collection(collection_name).document(phone)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                last_updated = data.get('last_updated')
                if last_updated:
                    if hasattr(last_updated, 'isoformat'):
                        return last_updated.isoformat()
                    else:
                        return str(last_updated)
    except Exception as e:
        logging.error(f"Error getting last_updated timestamp from {collection_name}: {e}")
    return None

def get_cached_insights(phone, max_age_minutes=1440):
    return FirebaseUserInsights.get_cached_insights(phone, max_age_minutes)

def set_cached_insights(phone, insights):
    return FirebaseUserInsights.set_cached_insights(phone, insights)

def get_user_goals(phone):
    return FirebaseUserGoals.get_user_goals(phone)

def set_user_goals(phone, goals):
    return FirebaseUserGoals.set_user_goals(phone, goals)

def get_chat_history(phone, days=7):
    return FirebaseUserChatHistory.get_chat_history(phone, days)

def add_chat_message(phone, role, text):
    return FirebaseUserChatHistory.add_chat_message(phone, role, text)

def get_cached_health_score(phone, max_age_minutes=1440):
    return FirebaseUserHealthScore.get_cached_health_score(phone, max_age_minutes)

def set_cached_health_score(phone, health_score):
    return FirebaseUserHealthScore.set_cached_health_score(phone, health_score)

def get_cached_goal_insights(phone, max_age_minutes=1440):
    return FirebaseUserGoalInsights.get_cached_goal_insights(phone, max_age_minutes)

def set_cached_goal_insights(phone, goal_insights):
    return FirebaseUserGoalInsights.set_cached_goal_insights(phone, goal_insights)

def get_user_profile(phone):
    return FirebaseUserProfile.get_user_profile(phone)

def update_user_profile(phone, profile_data):
    return FirebaseUserProfile.update_user_profile(phone, profile_data)

# Cash assets and transactions functions using Firebase
def get_user_cash_assets(phone):
    """Get user cash assets from Firestore"""
    try:
        db = get_firestore_db()
        if not db:
            return []
        
        # Query cash assets for the user - simplified to avoid index requirement
        query = db.collection(COLLECTIONS['user_cash_assets'])\
                 .where(field_path='phone', op_string='==', value=phone)
        
        assets = []
        for doc in query.stream():
            data = doc.to_dict()
            assets.append({
                'id': doc.id,
                'amount': data.get('amount', 0),
                'description': data.get('description', ''),
                'timestamp': data.get('timestamp')
            })
        
        # Sort in Python instead of Firestore to avoid index requirement
        assets.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return assets
    except Exception as e:
        print(f"Error getting user cash assets: {e}")
        return []

def add_user_cash_asset(phone, amount, description):
    """Add user cash asset to Firestore"""
    try:
        db = get_firestore_db()
        if not db:
            return False
        
        doc_ref = db.collection(COLLECTIONS['user_cash_assets']).document()
        asset = {
            'phone': phone,
            'amount': amount,
            'description': description,
            'timestamp': datetime.now(timezone.utc)
        }
        doc_ref.set(asset)
        # Add as credit transaction
        FirebaseUserCashTransaction.add_transaction(phone, amount, description, 'credit')
        asset['id'] = doc_ref.id
        return asset
    except Exception as e:
        print(f"Error adding user cash asset: {e}")
        return False

def delete_user_cash_asset(phone, asset_id):
    """Delete user cash asset from Firestore"""
    try:
        db = get_firestore_db()
        if not db:
            return False
        
        # Get the document reference
        doc_ref = db.collection(COLLECTIONS['user_cash_assets']).document(asset_id)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            if data.get('phone') == phone:
                doc_ref.delete()
                # Add as debit transaction
                FirebaseUserCashTransaction.add_transaction(phone, data.get('amount'), data.get('description'), 'debit')
                return True
        
        return False
    except Exception as e:
        print(f"Error deleting user cash asset: {e}")
        return False

@app.route('/cash-transactions', methods=['GET'])
def cash_transactions():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    txns = FirebaseUserCashTransaction.get_transactions(phone)
    # Format timestamps as ISO
    for t in txns:
        if t['timestamp']:
            t['timestamp'] = t['timestamp'].isoformat() if hasattr(t['timestamp'], 'isoformat') else str(t['timestamp'])
    return jsonify({'transactions': txns})

@app.route('/goals', methods=['GET', 'POST'])
def user_goals():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    if request.method == 'POST':
        goals = request.json.get('goals', [])
        if set_user_goals(phone, goals):
            return jsonify({'success': True, 'goals': goals})
        else:
            return jsonify({'error': 'Failed to save goals'}), 500
    else:
        goals = get_user_goals(phone)
        return jsonify({'goals': goals})

@app.route('/insights', methods=['GET', 'POST'])
def insights():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    # Support POSTed goals for goal-based insights
    goals = None
    if request.method == 'POST':
        try:
            goals = request.json.get('goals')
            if goals is not None:
                set_user_goals(phone, goals)
        except Exception:
            goals = None
    
    # For GET requests, check if user has existing goals for goal-based insights
    if request.method == 'GET' and not goals:
        try:
            existing_goals = get_user_goals(phone)
            if existing_goals and isinstance(existing_goals, list) and len(existing_goals) > 0:
                goals = existing_goals
        except Exception:
            goals = None

    refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # Handle goal-based insights caching (only if goals are present)
    if goals and (isinstance(goals, list) and len(goals) > 0):
        # Check if goals have changed by comparing with stored goals
        stored_goals = get_user_goals(phone)
        goals_changed = False
        
        if stored_goals and isinstance(stored_goals, list):
            # Compare current goals with stored goals
            if len(goals) != len(stored_goals):
                goals_changed = True
            else:
                # Compare each goal
                for i, goal in enumerate(goals):
                    if i >= len(stored_goals) or goal != stored_goals[i]:
                        goals_changed = True
                        break
        else:
            goals_changed = True
        
        # If goals have changed, force refresh to get new insights
        if goals_changed:
            refresh = True
        
        cached = None if refresh else get_cached_goal_insights(phone)
        if cached:
            last_updated = get_firebase_last_updated(COLLECTIONS['user_goal_insights'], phone)
            return jsonify({
                'insights': cached, 
                'cached': True,
                'last_updated': last_updated or datetime.now(timezone.utc).isoformat()
            })
    else:
        # Handle general insights caching (works without goals)
        cached = None if refresh else get_cached_insights(phone)
        if cached:
            last_updated = get_firebase_last_updated(COLLECTIONS['user_insights'], phone)
            return jsonify({
                'insights': cached, 
                'cached': True,
                'last_updated': last_updated or datetime.now(timezone.utc).isoformat()
            })

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

    prompt = (
        "Act as a top-tier Indian financial advisor and tax expert. "
        "Given the user's financial data below, "
        + ("and the user's stated financial goals, " if goals else "")
        + "generate a JSON array of 3-5 proactive, actionable insights or alerts. "
        "Each insight should have: title, priority (High/Medium/Low/Opportunity/Informational), description, action (short CTA), save (potential savings or benefit, if any), and a suggested icon (choose from: 'tax', 'portfolio', 'spending', 'opportunity', 'alert'). "
        "Focus on Indian tax-saving, investment optimization, risk, and wealth-building opportunities, "
        "as well as goal achievement, expenditure analysis, and portfolio performance. "
        "Respond ONLY with a JSON array, no extra text.\n"
        f"User financial data: {user_data}\n"
        + (f"User goals: {goals}\n" if goals else "")
    )
    gemini_payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        gemini_resp = requests.post(GEMINI_API_URL, json=gemini_payload)
        if gemini_resp.status_code != 200:
            logging.error(f"Gemini API error: {gemini_resp.status_code} {gemini_resp.text}")
            return jsonify({"error": "Gemini API error", "details": gemini_resp.text}), 500
        candidates = gemini_resp.json().get('candidates', [])
        if candidates:
            text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            try:
                # Remove Markdown code block markers if present
                cleaned_text = text.strip()
                if cleaned_text.startswith('```'):
                    cleaned_text = re.sub(r'^```[a-zA-Z]*\s*', '', cleaned_text)
                    cleaned_text = re.sub(r'```$', '', cleaned_text)
                    cleaned_text = cleaned_text.strip()
                insights = json.loads(cleaned_text)
                if goals and (isinstance(goals, list) and len(goals) > 0):
                    set_cached_goal_insights(phone, insights)
                    last_updated = get_firebase_last_updated(COLLECTIONS['user_goal_insights'], phone)
                else:
                    set_cached_insights(phone, insights)
                    last_updated = get_firebase_last_updated(COLLECTIONS['user_insights'], phone)
                
                return jsonify({
                    "insights": insights, 
                    'cached': False,
                    'last_updated': last_updated or datetime.now(timezone.utc).isoformat()
                })
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse Gemini response as JSON: {e}")
                return jsonify({"error": "Failed to parse AI response"}), 500
        else:
            return jsonify({"error": "No response from Gemini API"}), 500
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to get insights"}), 500

@app.route('/health-score', methods=['GET', 'POST'])
def health_score():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    # Check for refresh parameter from query string
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # Accept optional goals from frontend
    goals = request.json.get('goals') if request.is_json else None

    # Check cache first (unless refresh is requested)
    if not refresh:
        cached = get_cached_health_score(phone)
        if cached:
            # Get the last updated timestamp from Firebase
            last_updated = get_firebase_last_updated(COLLECTIONS['user_health_score'], phone)
            if last_updated:
                cached['last_updated'] = last_updated
            
            return jsonify(cached)

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

    prompt = (
        "Act as a top-tier Indian financial advisor. "
        "Given the user's financial data below, "
        + ("and the user's stated financial goals, " if goals else "")
        + "analyze and return a JSON object with: "
        "'score' (overall health score, 0-100), and 'metrics' (an array of objects, each with 'label', 'value' (0-100), and 'explanation'). "
        "Metrics should include: Emergency Fund, Debt Management, Retirement Planning, Insurance Coverage, Tax Efficiency. "
        "Be concise and accurate. Respond ONLY with the JSON object, no extra text.\n"
        f"User financial data: {user_data}\n"
        + (f"User goals: {goals}\n" if goals else "")
    )
    gemini_payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        gemini_resp = requests.post(GEMINI_API_URL, json=gemini_payload)
        if gemini_resp.status_code != 200:
            logging.error(f"Gemini API error: {gemini_resp.status_code} {gemini_resp.text}")
            return jsonify({"error": "Gemini API error", "details": gemini_resp.text}), 500
        candidates = gemini_resp.json().get('candidates', [])
        if candidates:
            text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            try:
                # Remove Markdown code block markers if present
                cleaned_text = text.strip()
                if cleaned_text.startswith('```'):
                    cleaned_text = re.sub(r'^```[a-zA-Z]*\s*', '', cleaned_text)
                    cleaned_text = re.sub(r'```$', '', cleaned_text)
                    cleaned_text = cleaned_text.strip()
                result = json.loads(cleaned_text)
                # Cache the result
                set_cached_health_score(phone, result)
                
                # Get the last updated timestamp for the response
                last_updated = get_firebase_last_updated(COLLECTIONS['user_health_score'], phone)
                if last_updated:
                    result['last_updated'] = last_updated
                
                return jsonify(result)
            except Exception as e:
                logging.error(f"Failed to parse Gemini health score JSON: {e}\nRaw text: {text}")
                return jsonify({"error": "Failed to parse Gemini health score JSON", "raw": text}), 500
        return jsonify({"error": "No candidates from Gemini", "raw": gemini_resp.json()}), 500
    except Exception as e:
        logging.exception("Error calling Gemini API for health score")
        return jsonify({"error": "Exception calling Gemini API", "details": str(e)}), 500

@app.route('/cash-asset', methods=['GET', 'POST', 'DELETE'])
def cash_asset():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    if request.method == 'POST':
        data = request.json
        amount = data.get('amount')
        description = data.get('description', '')
        if amount is None:
            return jsonify({'error': 'Amount is required'}), 400
        if add_user_cash_asset(phone, amount, description):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to add cash asset'}), 500
    elif request.method == 'DELETE':
        asset_id = request.args.get('id')
        if not asset_id:
            return jsonify({'error': 'Asset ID is required'}), 400
        if delete_user_cash_asset(phone, asset_id):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to delete cash asset'}), 500
    else:
        assets = get_user_cash_assets(phone)
        return jsonify({'assets': assets})

@app.route('/mcp/<filename>')
def serve_mock_data(filename):
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    
    file_path = os.path.join(TEST_DATA_DIR, phone, filename)
    if os.path.exists(file_path):
        return send_from_directory(os.path.join(TEST_DATA_DIR, phone), filename)
    else:
        abort(404)

@app.route('/chat-history', methods=['GET'])
def get_chat_history_endpoint():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    
    days = request.args.get('days', 7, type=int)
    history = get_chat_history(phone, days)
    return jsonify({'history': history})

@app.route('/chatbot', methods=['POST'])
def chatbot():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Get last 7 days chat history from DB
    chat_history_db = get_chat_history(phone, days=7)
    chat_history = [{'role': msg['role'], 'text': msg['text']} for msg in chat_history_db]
    
    # First, analyze if the message requires financial data
    analysis_prompt = f"""
    Analyze this user message and determine if it requires access to the user's financial data.
    
    User message: "{user_message}"
    
    Respond with ONLY a JSON object:
    {{
        "requires_financial_data": true/false,
        "reason": "brief explanation",
        "response_type": "financial_analysis" or "general_conversation" or "greeting" or "help"
    }}
    
    Examples:
    - "Hi" → requires_financial_data: false, response_type: "greeting"
    - "How are you?" → requires_financial_data: false, response_type: "general_conversation"
    - "What's my portfolio performance?" → requires_financial_data: true, response_type: "financial_analysis"
    - "Help me with tax planning" → requires_financial_data: true, response_type: "financial_analysis"
    - "What's the weather like?" → requires_financial_data: false, response_type: "general_conversation"
    """
    
    try:
        # Analyze the message first
        analysis_payload = {
            "contents": [{"parts": [{"text": analysis_prompt}]}]
        }
        analysis_resp = requests.post(GEMINI_API_URL, json=analysis_payload)
        
        if analysis_resp.status_code != 200:
            logging.error(f"Gemini API error in analysis: {analysis_resp.status_code} {analysis_resp.text}")
            return jsonify({"error": "Gemini API error", "details": analysis_resp.text}), 500
        
        analysis_text = analysis_resp.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
        
        # Parse the analysis response
        try:
            # Clean up the response if it has markdown
            cleaned_text = analysis_text.strip()
            if cleaned_text.startswith('```'):
                cleaned_text = re.sub(r'^```[a-zA-Z]*\s*', '', cleaned_text)
                cleaned_text = re.sub(r'```$', '', cleaned_text)
                cleaned_text = cleaned_text.strip()
            
            analysis_result = json.loads(cleaned_text)
            requires_financial_data = analysis_result.get('requires_financial_data', False)
            response_type = analysis_result.get('response_type', 'general_conversation')
            
        except Exception as e:
            logging.error(f"Failed to parse analysis response: {e}")
            # Default to requiring financial data if parsing fails
            requires_financial_data = True
            response_type = 'financial_analysis'
        
        # Fetch user data only if needed
        user_data = {}
        if requires_financial_data:
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
        
        # Get user profile for personalized responses
        user_profile = get_user_profile(phone)
        user_name = user_profile.name if user_profile else 'User'
        
        # Generate appropriate response based on type
        if response_type == 'greeting':
            response_prompt = f"""
            You are ArthaPandit, a friendly and knowledgeable financial expert AI assistant. 
            The user's name is {user_name}.
            
            Respond to this greeting in a warm, professional manner. Introduce yourself briefly as ArthaPandit and mention that you can help with financial planning, investment advice, tax optimization, and general financial questions.
            
            User message: "{user_message}"
            
            Keep your response friendly, concise (2-3 sentences), and professional.
            """
        elif response_type == 'general_conversation':
            response_prompt = f"""
            You are ArthaPandit, a friendly and knowledgeable financial expert AI assistant. 
            The user's name is {user_name}.
            
            Respond to this general conversation naturally, but always try to gently steer the conversation toward financial topics when appropriate. You can discuss general topics but maintain your identity as a financial expert.
            
            User message: "{user_message}"
            
            Keep your response conversational, helpful, and try to connect it to financial wellness when possible.
            """
        elif response_type == 'help':
            response_prompt = f"""
            You are ArthaPandit, a friendly and knowledgeable financial expert AI assistant. 
            The user's name is {user_name}.
            
            Provide helpful information about what you can do. You can help with:
            - Portfolio analysis and investment advice
            - Tax planning and optimization
            - Financial goal setting and tracking
            - Budget analysis and spending optimization
            - Insurance and risk management
            - Retirement planning
            - General financial education
            
            User message: "{user_message}"
            
            Provide a comprehensive but concise overview of your capabilities.
            """
        else:  # financial_analysis
            # Add the new user message to the history for context
            chat_history.append({'role': 'user', 'text': user_message})
            history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['text']}" for msg in chat_history[-6:]])  # Last 6 messages for context
            
            response_prompt = f"""
            You are ArthaPandit, a top-tier Indian financial advisor and wealth manager. 
            The user's name is {user_name}.
            
            Analyze the user's financial data and provide personalized, actionable advice. Be specific, practical, and focus on Indian financial context (tax laws, investment options, etc.).
            
            User financial data: {user_data}
            Recent conversation history: {history_text}
            
            Provide detailed, personalized financial advice based on the user's actual data. Include specific recommendations, potential savings/benefits, and actionable steps.
            """
        
        # Generate the response
        response_payload = {
            "contents": [{"parts": [{"text": response_prompt}]}]
        }
        response_resp = requests.post(GEMINI_API_URL, json=response_payload)
        
        if response_resp.status_code != 200:
            logging.error(f"Gemini API error in response: {response_resp.status_code} {response_resp.text}")
            return jsonify({"error": "Gemini API error", "details": response_resp.text}), 500
        
        gemini_text = response_resp.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', str(response_resp.json()))
        
        # Store user and assistant messages in DB
        add_chat_message(phone, 'user', user_message)
        add_chat_message(phone, 'assistant', gemini_text)
        
        # Return last 7 days history (including the new ones)
        chat_history_db = get_chat_history(phone, days=7)
        chat_history = [{'role': msg['role'], 'text': msg['text']} for msg in chat_history_db]
        
        return jsonify({
            "response": gemini_text, 
            "history": chat_history,
            "response_type": response_type,
            "requires_financial_data": requires_financial_data
        })
        
    except Exception as e:
        logging.exception("Error calling Gemini API")
        return jsonify({"error": "Exception calling Gemini API", "details": str(e)}), 500

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    # Get conversation context
    conversation_context = request.json.get('context', '')
    is_initial = request.json.get('is_initial', False)
    
    # Fetch user data for personalized questions
    user_data = {}
    if not is_initial:
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

    # Get user profile for personalization
    user_profile = get_user_profile(phone)
    user_name = user_profile.get('name', 'User') if isinstance(user_profile, dict) else getattr(user_profile, 'name', 'User')
    
    if is_initial:
        # Generate initial questions
        prompt = f"""
        You are ArthaPandit, a financial expert AI assistant. Generate exactly 3 engaging \"what if\" scenario simulation questions to start a conversation with a user about their finances.
        
        User name: {user_name}
        
        Generate questions that are specific \"what if\" scenarios like:
        - \"What if I increase my SIP by ₹5,000?\"
        - \"What if I retire at 50?\"
        - \"What if I invest ₹10,000 more in mutual funds?\"
        - \"What if I buy a house worth ₹50 lakhs?\"
        - \"What if I start a ₹20,000 monthly SIP?\"
        - \"What if I invest ₹5 lakhs in stocks?\"
        
        Focus on:
        1. SIP/Investment amount changes
        2. Retirement age scenarios
        3. Major purchase scenarios (house, car, etc.)
        4. Investment allocation changes
        5. Tax-saving scenarios
        
        Make them specific with actual amounts and realistic scenarios for Indian context.
        
        Respond with ONLY a JSON array of exactly 3 questions, no extra text:
        [
            \"What if I increase my SIP by ₹5,000?\",
            \"What if I retire at 50?\",
            \"What if I invest ₹10,000 more in mutual funds?\"
        ]
        """
    else:
        # Generate follow-up questions based on conversation context
        prompt = f"""
        You are ArthaPandit, a financial expert AI assistant. Based on the recent conversation context, generate exactly 3 relevant \"what if\" scenario simulation questions.
        
        User name: {user_name}
        Recent conversation: {conversation_context}
        User financial data: {user_data}
        
        Generate \"what if\" questions that:
        1. Are directly related to what was just discussed
        2. Explore different scenarios based on the topic
        3. Suggest realistic \"what if\" variations
        
        Examples of good follow-up \"what if\" questions:
        - If discussing SIP: \"What if I increase my SIP by ₹3,000 more?\"
        - If discussing retirement: \"What if I retire at 45 instead?\"
        - If discussing investments: \"What if I invest ₹5 lakhs in stocks?\"
        - If discussing tax: \"What if I invest ₹1.5 lakhs in ELSS?\"
        
        Make them specific with actual amounts and realistic scenarios.
        
        Respond with ONLY a JSON array of exactly 3 questions, no extra text:
        [
            \"What if I increase my SIP by ₹3,000?\",
            \"What if I invest ₹5 lakhs in stocks?\",
            \"What if I retire at 45?\"
        ]
        """
    
    gemini_payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        gemini_resp = requests.post(GEMINI_API_URL, json=gemini_payload)
        if gemini_resp.status_code != 200:
            logging.error(f"Gemini API error: {gemini_resp.status_code} {gemini_resp.text}")
            return jsonify({"error": "Gemini API error", "details": gemini_resp.text}), 500
        
        candidates = gemini_resp.json().get('candidates', [])
        if candidates:
            text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            try:
                # Clean up the response if it has markdown
                cleaned_text = text.strip()
                if cleaned_text.startswith('```'):
                    cleaned_text = re.sub(r'^```[a-zA-Z]*\s*', '', cleaned_text)
                    cleaned_text = re.sub(r'```$', '', cleaned_text)
                    cleaned_text = cleaned_text.strip()
                
                questions = json.loads(cleaned_text)
                # Ensure all questions start with 'What if I' and limit to 3
                filtered = [q if q.lower().startswith('what if i') else f"What if I {q[0].lower() + q[1:]}" for q in questions]
                return jsonify({"questions": filtered[:3]})
            except Exception as e:
                logging.error(f"Failed to parse Gemini questions JSON: {e}\nRaw text: {text}")
                # Return default questions if parsing fails
                default_questions = [
                    "What's my current financial health score?",
                    "How can I optimize my tax savings?",
                    "What investment opportunities should I consider?"
                ]
                return jsonify({"questions": default_questions})
        
        return jsonify({"error": "No candidates from Gemini", "raw": gemini_resp.json()}), 500
    except Exception as e:
        logging.exception("Error calling Gemini API for questions")
        return jsonify({"error": "Exception calling Gemini API", "details": str(e)}), 500

# News and profile functions using Firebase
def get_cached_news(phone, max_age_minutes=1440):
    """Get cached news from Firestore"""
    return FirebaseUserNews.get_cached_news(phone, max_age_minutes)

def set_cached_news(phone, news_items):
    """Cache news in Firestore"""
    return FirebaseUserNews.set_cached_news(phone, news_items)

@app.route('/news', methods=['GET'])
def investment_insights():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # Check cache first
    if not refresh:
        cached = get_cached_news(phone)
        if cached:
            last_updated = get_firebase_last_updated(COLLECTIONS['user_news'], phone)
            return jsonify({
                'news': cached,
                'cached': True,
                'last_updated': last_updated or datetime.now(timezone.utc).isoformat()
            })

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

    today_str = datetime.now().strftime('%Y-%m-%d')
    last_7_days_str = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # Build a prompt for Gemini
    prompt = (
        f"You are a financial news assistant. Given the user's investment holdings below (mutual funds, stocks, etc.), "
        f"generate a JSON array of 3-7 highly relevant, recent, and personalized news headlines or updates for each holding. "
        f"Only include news from the last 7 days (today is {today_str}, only include news dated {last_7_days_str} to {today_str}). "
        f"If there is no news for a holding in the last 7 days, do not include it. "
        f"For each news item, include: title, summary, date (YYYY-MM-DD), holdingName (the fund/stock/etc.), and a link (if possible). "
        f"Focus on news that would matter to an Indian investor, such as fund performance, regulatory changes, management updates, major market moves, or anything that could impact the user's portfolio. "
        f"Respond ONLY with a JSON array, no extra text.\n"
        f"User investment data: {user_data}\n"
    )
    
    gemini_payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        gemini_resp = requests.post(GEMINI_API_URL, json=gemini_payload)
        if gemini_resp.status_code != 200:
            logging.error(f"Gemini API error: {gemini_resp.status_code} {gemini_resp.text}")
            return jsonify({"error": "Gemini API error", "details": gemini_resp.text}), 500
        
        candidates = gemini_resp.json().get('candidates', [])
        if candidates:
            text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            try:
                # Remove Markdown code block markers if present
                cleaned_text = text.strip()
                if cleaned_text.startswith('```'):
                    cleaned_text = re.sub(r'^```[a-zA-Z]*\s*', '', cleaned_text)
                    cleaned_text = re.sub(r'```$', '', cleaned_text)
                    cleaned_text = cleaned_text.strip()
                news_items = json.loads(cleaned_text)
                set_cached_news(phone, news_items)
                
                last_updated = get_firebase_last_updated(COLLECTIONS['user_news'], phone)
                return jsonify({
                    'news': news_items,
                    'cached': False,
                    'last_updated': last_updated or datetime.now(timezone.utc).isoformat()
                })
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse Gemini response as JSON: {e}")
                return jsonify({"error": "Failed to parse AI response"}), 500
        else:
            return jsonify({"error": "No response from Gemini API"}), 500
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to get news"}), 500

@app.route('/profile', methods=['GET', 'PUT'])
def user_profile():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    def format_datetime(dt_value):
        """Helper function to format datetime values from Firebase"""
        if dt_value is None:
            return None
        if hasattr(dt_value, 'isoformat'):
            return dt_value.isoformat()
        elif isinstance(dt_value, str):
            return dt_value
        else:
            return str(dt_value)

    if request.method == 'GET':
        profile = get_user_profile(phone)
        if profile:
            return jsonify({
                'name': profile.name,
                'email': profile.email,
                'date_of_birth': format_datetime(profile.date_of_birth),
                'occupation': profile.occupation,
                'address': profile.address,
                'emergency_contact': profile.emergency_contact,
                'risk_profile': profile.risk_profile,
                'investment_goals': profile.investment_goals,
                'created_at': format_datetime(profile.created_at),
                'updated_at': format_datetime(profile.updated_at)
            })
        else:
            return jsonify({'error': 'Failed to get profile'}), 500
    
    elif request.method == 'PUT':
        data = request.json
        try:
            # Handle date conversion
            if 'date_of_birth' in data and data['date_of_birth']:
                data['date_of_birth'] = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            
            profile = update_user_profile(phone, data)
            if profile:
                return jsonify({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'profile': {
                        'name': profile.name,
                        'email': profile.email,
                        'date_of_birth': format_datetime(profile.date_of_birth),
                        'occupation': profile.occupation,
                        'address': profile.address,
                        'emergency_contact': profile.emergency_contact,
                        'risk_profile': profile.risk_profile,
                        'investment_goals': profile.investment_goals,
                        'updated_at': format_datetime(profile.updated_at)
                    }
                })
            else:
                return jsonify({'error': 'Failed to update profile'}), 500
        except Exception as e:
            return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('FLASK_PORT', 8080))) 