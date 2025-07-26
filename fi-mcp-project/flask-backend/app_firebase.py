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
    FirebaseUserHealthScore, FirebaseUserGoalInsights, FirebaseUserProfile
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

# Firebase-based functions (replacing SQLite functions)
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
        
        # Query cash assets for the user
        query = db.collection(COLLECTIONS['user_cash_assets'])\
                 .where('phone', '==', phone)\
                 .order_by('timestamp', direction='desc')
        
        assets = []
        for doc in query.stream():
            data = doc.to_dict()
            assets.append({
                'id': doc.id,
                'amount': data.get('amount', 0),
                'description': data.get('description', ''),
                'timestamp': data.get('timestamp')
            })
        
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
        
        db.collection(COLLECTIONS['user_cash_assets']).add({
            'phone': phone,
            'amount': amount,
            'description': description,
            'timestamp': datetime.now(timezone.utc)
        })
        return True
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
                return True
        
        return False
    except Exception as e:
        print(f"Error deleting user cash asset: {e}")
        return False

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

    refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # Handle goal-based insights caching
    if goals:
        cached = None if refresh else get_cached_goal_insights(phone)
        if cached:
            return jsonify({
                'insights': cached, 
                'cached': True,
                'last_updated': datetime.now(timezone.utc).isoformat()
            })
    else:
        # Handle general insights caching
        cached = None if refresh else get_cached_insights(phone)
        if cached:
            return jsonify({
                'insights': cached, 
                'cached': True,
                'last_updated': datetime.now(timezone.utc).isoformat()
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
                if goals:
                    set_cached_goal_insights(phone, insights)
                else:
                    set_cached_insights(phone, insights)
                
                return jsonify({
                    "insights": insights, 
                    'cached': False,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                })
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse Gemini response as JSON: {e}")
                return jsonify({"error": "Failed to parse AI response"}), 500
        else:
            return jsonify({"error": "No response from Gemini API"}), 500
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to get insights"}), 500

@app.route('/health-score', methods=['POST'])
def health_score():
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
        "Act as a financial health expert. "
        "Given the user's financial data below, generate a comprehensive financial health score and analysis. "
        "Respond with a JSON object containing: "
        "score (0-100), category (Excellent/Good/Fair/Poor), breakdown (object with scores for different aspects), "
        "strengths (array of positive points), weaknesses (array of areas to improve), "
        "recommendations (array of specific actions to improve score), and overall_analysis (detailed explanation). "
        "Focus on Indian financial context including savings, investments, debt management, emergency funds, and financial planning. "
        "Respond ONLY with a JSON object, no extra text.\n"
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
                health_score_data = json.loads(cleaned_text)
                set_cached_health_score(phone, health_score_data)
                return jsonify(health_score_data)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse Gemini response as JSON: {e}")
                return jsonify({"error": "Failed to parse AI response"}), 500
        else:
            return jsonify({"error": "No response from Gemini API"}), 500
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to get health score"}), 500

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

    # Get last 7 days chat history from Firebase
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
        analysis_resp = requests.post(GEMINI_API_URL, json={
            "contents": [{"parts": [{"text": analysis_prompt}]}]
        })
        
        if analysis_resp.status_code == 200:
            analysis_candidates = analysis_resp.json().get('candidates', [])
            if analysis_candidates:
                analysis_text = analysis_candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                try:
                    analysis = json.loads(analysis_text.strip())
                    requires_financial_data = analysis.get('requires_financial_data', False)
                except:
                    requires_financial_data = True  # Default to requiring data if analysis fails
            else:
                requires_financial_data = True
        else:
            requires_financial_data = True
    except:
        requires_financial_data = True

    # Build context based on whether financial data is needed
    if requires_financial_data:
        # Get user's financial data
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
        
        context = f"""
        You are a professional Indian financial advisor. The user has provided their financial data below.
        Use this data to provide personalized, accurate financial advice.
        
        User's Financial Data: {user_data}
        
        User's Message: {user_message}
        
        Provide a helpful, actionable response based on their financial situation.
        """
    else:
        context = f"""
        You are a helpful financial assistant. The user is asking a general question.
        
        User's Message: {user_message}
        
        Provide a friendly, helpful response. If they ask about financial topics, 
        encourage them to share their financial data for personalized advice.
        """

    # Build the full prompt with chat history
    system_prompt = DEFAULT_SYSTEM_INSTRUCTION
    full_prompt = f"{system_prompt}\n\n{context}"
    
    # Add chat history if available
    if chat_history:
        history_text = "\n".join([f"{msg['role']}: {msg['text']}" for msg in chat_history[-10:]])  # Last 10 messages
        full_prompt = f"{full_prompt}\n\nRecent conversation:\n{history_text}\n\nAssistant:"

    gemini_payload = {
        "contents": [{"parts": [{"text": full_prompt}]}]
    }
    
    try:
        gemini_resp = requests.post(GEMINI_API_URL, json=gemini_payload)
        if gemini_resp.status_code != 200:
            logging.error(f"Gemini API error: {gemini_resp.status_code} {gemini_resp.text}")
            return jsonify({"error": "Gemini API error", "details": gemini_resp.text}), 500
        
        candidates = gemini_resp.json().get('candidates', [])
        if candidates:
            assistant_message = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            # Save both messages to Firebase
            add_chat_message(phone, 'user', user_message)
            add_chat_message(phone, 'assistant', assistant_message)
            
            return jsonify({
                "response": assistant_message,
                "requires_financial_data": requires_financial_data
            })
        else:
            return jsonify({"error": "No response from Gemini API"}), 500
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to get response"}), 500

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
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
        "Act as a financial advisor. Based on the user's financial data below, "
        "generate 5-8 relevant, insightful questions that would help understand their financial goals, "
        "concerns, or areas they want to improve. "
        "Questions should be specific to their financial situation and encourage deeper thinking. "
        "Respond with ONLY a JSON array of question strings, no extra text.\n"
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
                questions = json.loads(cleaned_text)
                return jsonify({"questions": questions})
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse Gemini response as JSON: {e}")
                return jsonify({"error": "Failed to parse AI response"}), 500
        else:
            return jsonify({"error": "No response from Gemini API"}), 500
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to generate questions"}), 500

# News and profile functions using Firebase
def get_cached_news(phone, max_age_minutes=1440):
    """Get cached news from Firestore"""
    try:
        db = get_firestore_db()
        if not db:
            return None
            
        doc_ref = db.collection(COLLECTIONS['user_news']).document(phone)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            last_updated = data.get('last_updated')
            if last_updated:
                if hasattr(last_updated, 'timestamp'):
                    last_updated = datetime.fromtimestamp(last_updated.timestamp(), tz=timezone.utc)
                
                age = datetime.now(timezone.utc) - last_updated
                if age.total_seconds() < max_age_minutes * 60:
                    return json.loads(data.get('news_json', '[]'))
        return None
    except Exception as e:
        print(f"Error getting cached news: {e}")
        return None

def set_cached_news(phone, news_items):
    """Cache news in Firestore"""
    try:
        db = get_firestore_db()
        if not db:
            return False
            
        doc_ref = db.collection(COLLECTIONS['user_news']).document(phone)
        doc_ref.set({
            'phone': phone,
            'news_json': json.dumps(news_items),
            'last_updated': datetime.now(timezone.utc)
        })
        return True
    except Exception as e:
        print(f"Error setting cached news: {e}")
        return False

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
            return jsonify({
                'news': cached,
                'cached': True,
                'last_updated': datetime.now(timezone.utc).isoformat()
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
        "Act as a financial news analyst and investment expert. "
        "Based on the user's financial data below, generate 3-5 personalized investment insights and news recommendations. "
        "Each insight should be relevant to their portfolio and financial situation. "
        "Respond with a JSON array where each item has: title, summary, relevance (why it matters to this user), "
        "action (what they should consider), category (market_update, tax_news, investment_opportunity, risk_alert), "
        "and impact (positive/neutral/negative). "
        "Focus on Indian markets, tax implications, and personal finance. "
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
                news_items = json.loads(cleaned_text)
                set_cached_news(phone, news_items)
                
                return jsonify({
                    'news': news_items,
                    'cached': False,
                    'last_updated': datetime.now(timezone.utc).isoformat()
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

    if request.method == 'PUT':
        profile_data = request.json
        if update_user_profile(phone, profile_data):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to update profile'}), 500
    else:
        profile = get_user_profile(phone)
        if profile:
            return jsonify(profile)
        else:
            return jsonify({'error': 'Failed to get profile'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('FLASK_PORT', 5001))) 