from flask import Flask, request, jsonify, session, send_from_directory, abort
from flask_cors import CORS
import requests
import os
import json
import logging
from dotenv import load_dotenv
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import uuid

# Import Google Cloud APIs
try:
    from google.cloud import speech
    from google.cloud import language_v1
except ImportError:
    logging.warning("Google Cloud Speech and Language APIs not available. Voice analysis will be limited.")
    speech = None
    language_v1 = None

# Import Firebase modules
from firebase_config import initialize_firebase, get_firestore_db, COLLECTIONS
from firebase_models import (
    FirebaseUserInsights, FirebaseUserGoals, FirebaseUserChatHistory,
    FirebaseUserHealthScore, FirebaseUserGoalInsights, FirebaseUserProfile,
    FirebaseUserNews, FirebaseUserCashTransaction
)

# Import ADK Financial Advisor Agent
from custom_financial_agent import CustomFinancialAgent

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize Firebase
initialize_firebase()

# Initialize ADK-Compliant Custom Financial Agent
custom_agent = CustomFinancialAgent()

# FI-MCP Server Configuration
FI_MCP_SERVER_URL = "http://localhost:8484/mcp/stream"

def authenticate_fi_mcp_session(phone: str) -> str:
    """
    Authenticate with fi-mcp server and get session ID
    """
    try:
        # Generate a session ID
        session_id = f"mcp-session-{str(uuid.uuid4())}"
        
        # Try to call a tool with the session ID to trigger authentication
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "fetch_bank_transactions",
                "arguments": {}  # Empty arguments object as per working endpoint
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        }
        
        response = requests.post(
            FI_MCP_SERVER_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'content' in result['result']:
                return session_id
        elif response.status_code == 400 and "Invalid session ID" in response.text:
            # This is expected - we need to authenticate via the login URL
            base_url = FI_MCP_SERVER_URL.replace("/mcp/stream", "")
            login_url = f"{base_url}/wealth-mcp-login?token={session_id}"
            logging.info(f"Authentication required. Login URL: {login_url}")
            return session_id
        
        logging.warning(f"Authentication failed for phone {phone}")
        return None
            
    except Exception as e:
        logging.error(f"Error authenticating with fi-mcp: {e}")
        return None

def fetch_fi_mcp_data(phone: str, data_type: str) -> dict:
    """
    Fetch financial data from fi-mcp server
    """
    try:
        # Generate a session ID for this request
        session_id = f"mcp-session-{str(uuid.uuid4())}"
        
        # Prepare the request payload for fi-mcp server using JSON-RPC 2.0 format
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": f"fetch_{data_type}",
                "arguments": {}  # Empty arguments object as per working endpoint
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        }
        
        response = requests.post(
            FI_MCP_SERVER_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'content' in result['result']:
                # Parse the content from fi-mcp response
                content = result['result']['content']
                
                # Check if this is an authentication required response
                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]
                    if isinstance(first_item, dict) and 'text' in first_item:
                        try:
                            text_content = json.loads(first_item['text'])
                            if text_content.get('status') == 'login_required':
                                logging.info(f"Authentication required for {data_type}. Session ID: {session_id}")
                                logging.info(f"Login URL: {text_content.get('login_url')}")
                                return None  # Return None to trigger fallback to mock data
                        except json.JSONDecodeError:
                            pass
                
                # If we have actual data, parse it
                if isinstance(content, str):
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        logging.warning(f"Could not parse JSON content for {data_type}")
                        return None
                elif isinstance(content, dict):
                    return content
                else:
                    logging.warning(f"Unexpected content format for {data_type}: {type(content)}")
                    return None
            else:
                logging.warning(f"Unexpected fi-mcp response format for {data_type}: {result}")
                return None
        elif response.status_code == 400 and "Invalid session ID" in response.text:
            # Authentication required - this is expected behavior
            logging.info(f"Authentication required for {data_type}. Session ID: {session_id}")
            return None
        else:
            logging.error(f"fi-mcp server error for {data_type}: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error fetching {data_type} from fi-mcp: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error for {data_type}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error fetching {data_type}: {e}")
        return None

def get_financial_data_from_fi_mcp(phone: str) -> dict:
    """
    Fetch all financial data from fi-mcp server
    """
    user_data = {}
    
    # Define the data types to fetch from fi-mcp
    data_types = [
        'mf_transactions',
        'stock_transactions', 
        'bank_transactions',
        'credit_report',
        'epf_details',
        'net_worth',
        'nominee_details',
        'insurance'
    ]
    
    for data_type in data_types:
        try:
            data = fetch_fi_mcp_data(phone, data_type)
            if data:
                user_data[f'fetch_{data_type}'] = data
                logging.info(f"Successfully fetched {data_type} for phone {phone}")
            else:
                logging.warning(f"No data received for {data_type} from fi-mcp")
                user_data[f'fetch_{data_type}'] = None
        except Exception as e:
            logging.error(f"Error fetching {data_type}: {e}")
            user_data[f'fetch_{data_type}'] = None
    
    return user_data

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

    try:
        # Try to fetch data from fi-mcp server first
        logging.info(f"Attempting to fetch financial data from fi-mcp server for phone: {phone}")
        user_data = get_financial_data_from_fi_mcp(phone)
        
        # Check if we got any data from fi-mcp
        has_fi_mcp_data = any(data is not None for data in user_data.values())
        
        if has_fi_mcp_data:
            logging.info(f"Successfully fetched data from fi-mcp server for phone: {phone}")
            return jsonify(user_data)
        else:
            logging.warning(f"No data received from fi-mcp server, falling back to mock data for phone: {phone}")
            
            # Fallback to mock data if fi-mcp server is not available
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
            
    except Exception as e:
        logging.error(f"Error in financial_data endpoint: {e}")
        # Fallback to mock data on any error
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

    # Get user goals for personalized recommendations
    user_goals = get_user_goals(phone)
    
    # Use Custom Financial Agent for advanced recommendations
    try:
        logging.info("🤖 RECOMMENDATIONS: Using Custom Financial Agent")
        recommendations = custom_agent.generate_recommendations(user_data, user_goals)
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        logging.error(f"❌ RECOMMENDATIONS: Error generating Custom recommendations: {e}")
        logging.info("🔄 RECOMMENDATIONS: Falling back to direct Gemini API")
        # Fallback to original method
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
        logging.info("🔗 RECOMMENDATIONS: Calling Gemini API directly (fallback)")
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

    # Use Custom agent for advanced insights
    try:
        logging.info("🎯 INSIGHTS: Using Custom Financial Agent")
        insights = custom_agent.generate_insights(user_data, goals)
        logging.info(f"✅ INSIGHTS: Custom agent generated {len(insights)} insights")
        
        # Cache the insights
        if goals and len(goals) > 0:
            set_cached_goal_insights(phone, insights)
        else:
            set_cached_insights(phone, insights)
        
        # Get the last updated timestamp
        collection_name = COLLECTIONS['user_goal_insights'] if goals else COLLECTIONS['user_insights']
        last_updated = get_firebase_last_updated(collection_name, phone)
        
        return jsonify({
            'insights': insights,
            'cached': False,
            'last_updated': last_updated or datetime.now(timezone.utc).isoformat(),
            'agent_type': 'custom_financial_agent'
        })
        
    except Exception as e:
        logging.error(f"❌ INSIGHTS: Error generating Custom agent insights: {e}")
        logging.info("🔄 INSIGHTS: Falling back to original method")
        
        # Fallback to original method
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

    # Use Custom agent for advanced health score calculation
    try:
        logging.info("🎯 HEALTH SCORE: Using Custom Financial Agent")
        health_score_data = custom_agent.calculate_health_score(user_data, goals)
        logging.info(f"✅ HEALTH SCORE: Custom agent calculated score: {health_score_data.get('score', 0)}")
        
        # Cache the result
        set_cached_health_score(phone, health_score_data)
        
        # Get the last updated timestamp for the response
        last_updated = get_firebase_last_updated(COLLECTIONS['user_health_score'], phone)
        if last_updated:
            health_score_data['last_updated'] = last_updated
        
        health_score_data['agent_type'] = 'custom_financial_agent'
        return jsonify(health_score_data)
        
    except Exception as e:
        logging.error(f"❌ HEALTH SCORE: Error calculating Custom agent health score: {e}")
        logging.info("🔄 HEALTH SCORE: Falling back to original method")
        
        # Fallback to original method
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

@app.route('/goal-suggestions', methods=['POST'])
def goal_suggestions():
    """Get intelligent goal suggestions based on user's financial profile"""
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        data = request.json
        user_message = data.get('message', '')
        goal_type = data.get('goal_type', 'general')
        
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

        # Get user profile and existing goals
        user_profile = get_user_profile(phone)
        existing_goals = get_user_goals(phone) or []
        
        user_profile_dict = {
            'name': user_profile.name if user_profile else 'User',
            'goals': existing_goals
        }

        # Use custom agent for intelligent goal suggestions
        try:
            logging.info("🎯 GOAL SUGGESTIONS: Using Custom Financial Agent")
            logging.info(f"📝 GOAL SUGGESTIONS: User message: {user_message}")
            logging.info(f"📊 GOAL SUGGESTIONS: Goal type: {goal_type}")
            logging.info(f"👤 GOAL SUGGESTIONS: User profile: {user_profile_dict}")
            logging.info(f"💰 GOAL SUGGESTIONS: Financial data keys: {list(user_data.keys())}")
            
            # Call custom agent with the user's actual message for goal analysis
            custom_response = custom_agent.analyze_financial_query(
                user_message=user_message,
                financial_data=user_data,
                user_profile=user_profile_dict
            )
            
            logging.info(f"🎯 GOAL SUGGESTIONS: Custom agent response received: {custom_response is not None}")
            if custom_response:
                logging.info(f"🎯 GOAL SUGGESTIONS: Agent type: {custom_response.get('agent_type', 'unknown')}")
                logging.info(f"🎯 GOAL SUGGESTIONS: Analysis type: {custom_response.get('analysis_type', 'unknown')}")
                logging.info(f"🎯 GOAL SUGGESTIONS: Response length: {len(custom_response.get('response', ''))}")
                logging.info(f"🎯 GOAL SUGGESTIONS: Recommendations count: {len(custom_response.get('recommendations', []))}")
            
            if custom_response and custom_response.get('response'):
                # Try to parse the response as JSON for structured suggestions
                try:
                    import re
                    # Extract JSON-like structure from the response
                    json_match = re.search(r'\{.*\}', custom_response['response'], re.DOTALL)
                    if json_match:
                        suggestions_data = json.loads(json_match.group())
                        suggestions = suggestions_data.get('suggestions', [])
                        logging.info(f"✅ GOAL SUGGESTIONS: JSON parsed successfully - {len(suggestions)} suggestions")
                        return jsonify({
                            'success': True,
                            'suggestions': suggestions,
                            'analysis': suggestions_data.get('analysis', ''),
                            'recommendations': suggestions_data.get('recommendations', []),
                            'agent_response': custom_response['response'],
                            'agent_type': 'custom_financial_agent'
                        })
                except Exception as e:
                    logging.warning(f"⚠️ GOAL SUGGESTIONS: JSON parsing failed: {e}")
                
                # If JSON parsing fails, check if the agent response has suggestions
                if 'suggestions' in custom_response:
                    suggestions = custom_response.get('suggestions', [])
                    logging.info(f"✅ GOAL SUGGESTIONS: Using agent suggestions - {len(suggestions)} suggestions")
                    return jsonify({
                        'success': True,
                        'suggestions': suggestions,
                        'analysis': custom_response.get('response', ''),
                        'recommendations': custom_response.get('recommendations', []),
                        'agent_response': custom_response['response'],
                        'agent_type': 'custom_financial_agent'
                    })
                else:
                    # Return the raw response
                    logging.info("📄 GOAL SUGGESTIONS: Using raw agent response")
                    return jsonify({
                        'success': True,
                        'suggestions': [],
                        'analysis': custom_response['response'],
                        'recommendations': custom_response.get('recommendations', []),
                        'agent_response': custom_response['response'],
                        'agent_type': 'custom_financial_agent'
                    })
            else:
                raise Exception("Invalid agent response")
                
        except Exception as e:
            logging.error(f"❌ GOAL SUGGESTIONS: Error in custom agent analysis: {e}")
            
            # Fallback to basic goal suggestions
            logging.info("🔄 GOAL SUGGESTIONS: Using fallback suggestions")
            fallback_suggestions = [
                {
                    "name": "Emergency Fund",
                    "type": "short",
                    "amount": 100000,
                    "year": datetime.now().year + 1,
                    "priority": "high",
                    "reasoning": "Essential for financial security",
                    "steps": ["Save ₹8,000 monthly", "Keep in high-yield savings"],
                    "challenges": ["Discipline to save regularly"],
                    "monthly_savings_needed": 8000
                },
                {
                    "name": "Retirement Planning",
                    "type": "long",
                    "amount": 5000000,
                    "year": datetime.now().year + 20,
                    "priority": "high",
                    "reasoning": "Long-term wealth building",
                    "steps": ["Start SIP in equity funds", "Increase contribution annually"],
                    "challenges": ["Market volatility", "Long-term commitment"],
                    "monthly_savings_needed": 15000
                }
            ]
            
            return jsonify({
                'success': True,
                'suggestions': fallback_suggestions,
                'analysis': 'Basic goal suggestions based on financial best practices',
                'recommendations': ['Start with emergency fund', 'Plan for retirement early'],
                'agent_response': 'Fallback suggestions provided',
                'agent_type': 'fallback'
            })
            
    except Exception as e:
        logging.error(f"❌ GOAL SUGGESTIONS: Error: {e}")
        return jsonify({'error': 'Failed to generate goal suggestions'}), 500

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
            
            # Use Custom Financial Agent for advanced financial analysis
            try:
                logging.info("🤖 CHATBOT: Using Custom Financial Agent")

                # Get user profile for personalized responses
                user_profile = get_user_profile(phone)
                user_profile_dict = {
                    'name': user_profile.name if user_profile else 'User',
                    'goals': get_user_goals(phone) if user_profile else []
                }

                # Use Custom agent for sophisticated analysis
                custom_response = custom_agent.analyze_financial_query(
                    user_message=user_message,
                    financial_data=user_data,
                    chat_history=chat_history,
                    user_profile=user_profile_dict
                )

                # Check if Custom response is valid
                if custom_response and custom_response.get('response'):
                    # Store user and assistant messages in DB
                    add_chat_message(phone, 'user', user_message)
                    add_chat_message(phone, 'assistant', custom_response['response'])

                    # Return enhanced response with Custom analysis
                    return jsonify({
                        "response": custom_response['response'],
                        "analysis_type": custom_response['analysis_type'],
                        "confidence": custom_response['confidence'],
                        "recommendations": custom_response['recommendations'],
                        "insights": custom_response['insights'],
                        "requires_financial_data": custom_response['requires_financial_data'],
                        "agent_type": custom_response.get('agent_type', 'custom_financial_agent')
                    })
                else:
                    raise Exception("Invalid Custom agent response")

            except Exception as e:
                logging.error(f"❌ CHATBOT: Error in Custom agent analysis: {e}")
                logging.info("🔄 CHATBOT: Falling back to direct Gemini API")
        
        # Fallback to original method (for both financial and non-financial queries)
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
        logging.info("🔗 CHATBOT: Calling Gemini API directly (fallback)")
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

# Google Cloud Speech-to-Text and Natural Language API setup
def setup_google_apis():
    """Setup Google Cloud APIs for voice analysis"""
    try:
        if speech is None or language_v1 is None:
            logging.warning("Google Cloud APIs not available")
            return None, None
            
        # Speech-to-Text client
        speech_client = speech.SpeechClient()
        
        # Natural Language client
        language_client = language_v1.LanguageServiceClient()
        
        return speech_client, language_client
    except Exception as e:
        logging.error(f"Failed to setup Google APIs: {e}")
        return None, None

def analyze_voice_recording(audio_content):
    """Analyze voice recording to extract borrower name, amount, and context"""
    try:
        speech_client, language_client = setup_google_apis()
        if not speech_client or not language_client:
            # Fallback when Google APIs are not available
            return {
                'transcript': 'Voice recording received (Google APIs not available)',
                'borrower_name': None,
                'borrower_phone': None,
                'amount': None,
                'purpose': None,
                'due_date': None,
                'confidence': 0.0
            }
        
        # Configure speech recognition
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-IN",
            enable_automatic_punctuation=True,
            enable_word_time_offsets=True
        )
        
        # Perform speech recognition
        response = speech_client.recognize(config=config, audio=audio)
        
        if not response.results:
            return {
                'transcript': 'No speech detected in recording',
                'borrower_name': None,
                'borrower_phone': None,
                'amount': None,
                'purpose': None,
                'due_date': None,
                'confidence': 0.0
            }
        
        # Extract transcribed text
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript
        
        # Analyze text using Natural Language API
        document = language_v1.Document(
            content=transcript,
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        
        # Analyze entities (names, amounts, etc.)
        entities_response = language_client.analyze_entities(document=document)
        
        # Extract information
        extracted_info = {
            'transcript': transcript,
            'borrower_name': None,
            'borrower_phone': None,
            'amount': None,
            'purpose': None,
            'due_date': None,
            'confidence': 0.0
        }
        
        # Extract entities
        for entity in entities_response.entities:
            if entity.type_ == language_v1.Entity.Type.PERSON:
                extracted_info['borrower_name'] = entity.name
            elif entity.type_ == language_v1.Entity.Type.NUMBER:
                # Check if it's likely an amount
                if 'rupee' in entity.name.lower() or 'rs' in entity.name.lower() or '₹' in entity.name:
                    extracted_info['amount'] = float(re.findall(r'\d+', entity.name)[0])
            elif entity.type_ == language_v1.Entity.Type.DATE:
                extracted_info['due_date'] = entity.name
        
        # Extract amount using regex patterns
        amount_patterns = [
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rupees?|rs|₹)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'rs\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*lakh',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*crore'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                if 'lakh' in match.group(0).lower():
                    extracted_info['amount'] = float(amount_str) * 100000
                elif 'crore' in match.group(0).lower():
                    extracted_info['amount'] = float(amount_str) * 10000000
                else:
                    extracted_info['amount'] = float(amount_str)
                break
        
        # Extract phone number using regex patterns
        phone_patterns = [
            r'(\d{10})',  # 10 digit phone number
            r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})',  # 3-3-4 format
            r'(\+\d{1,3}[-.\s]?\d{10})',  # International format
            r'phone\s*(?:number\s*)?(\d{10})',  # "phone 9876543210"
            r'call\s*(?:me\s*)?(?:at\s*)?(\d{10})',  # "call me at 9876543210"
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                phone = match.group(1).replace('-', '').replace('.', '').replace(' ', '')
                if len(phone) >= 10:
                    extracted_info['borrower_phone'] = phone
                    break
        
        # Calculate confidence score
        confidence = 0.0
        if extracted_info['borrower_name']:
            confidence += 0.25
        if extracted_info['borrower_phone']:
            confidence += 0.25
        if extracted_info['amount']:
            confidence += 0.3
        if extracted_info['purpose']:
            confidence += 0.1
        if extracted_info['due_date']:
            confidence += 0.1
        
        extracted_info['confidence'] = confidence
        
        return extracted_info
        
    except Exception as e:
        logging.error(f"Error analyzing voice recording: {e}")
        return {
            'transcript': 'Error analyzing voice recording',
            'borrower_name': None,
            'borrower_phone': None,
            'amount': None,
            'purpose': None,
            'due_date': None,
            'confidence': 0.0
        }

@app.route('/udhaar/voice-analyze', methods=['POST'])
def analyze_voice_for_lending():
    """Analyze voice recording for lending information"""
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        if 'voice_file' not in request.files:
            return jsonify({'error': 'No voice file provided'}), 400
        
        voice_file = request.files['voice_file']
        if voice_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read audio content
        audio_content = voice_file.read()
        
        # Analyze voice recording
        analysis_result = analyze_voice_recording(audio_content)
        
        if analysis_result:
            return jsonify({
                'success': True,
                'analysis': analysis_result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not analyze voice recording'
            })
        
    except Exception as e:
        logging.error(f"Error in voice analysis: {e}")
        return jsonify({'error': 'Failed to analyze voice recording'}), 500

@app.route('/udhaar/lend', methods=['POST'])
def lend_money():
    """Lend money to someone and record the transaction"""
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        data = request.json
        borrower_phone = data.get('borrower_phone', '')  # Optional now
        borrower_name = data.get('borrower_name')  # Required
        amount = data.get('amount')
        description = data.get('description', '')
        due_date = data.get('due_date')
        voice_note_url = data.get('voice_note_url', '')
        voice_analysis = data.get('voice_analysis', {})  # New field
        
        if not borrower_name or not amount:
            return jsonify({'error': 'Missing required fields: borrower_name and amount are required'}), 400
        
        # Add lending transaction to Firebase
        db = get_firestore_db()
        if db:
            lending_ref = db.collection(COLLECTIONS['user_lending']).add({
                'lender_phone': phone,
                'borrower_phone': borrower_phone,  # Can be empty
                'borrower_name': borrower_name,  # Store borrower name
                'amount': amount,
                'description': description,
                'due_date': due_date,
                'voice_note_url': voice_note_url,
                'voice_analysis': voice_analysis,  # Store voice analysis
                'status': 'active',  # active, repaid, overdue
                'created_at': datetime.now(timezone.utc),
                'trust_rating': None  # Will be set when repaid
            })
            
            return jsonify({
                'success': True,
                'lending_id': lending_ref[1].id,
                'message': f'Successfully lent ₹{amount} to {borrower_name}'
            })
        else:
            return jsonify({'error': 'Database connection failed'}), 500
            
    except Exception as e:
        logging.error(f"Error in lend_money: {e}")
        return jsonify({'error': 'Failed to record lending transaction'}), 500

@app.route('/udhaar/repay', methods=['POST'])
def repay_money():
    """Mark a lending transaction as repaid and set trust rating"""
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        data = request.json
        lending_id = data.get('lending_id')
        trust_rating = data.get('trust_rating', 5)  # 1-10 scale
        trust_level = data.get('trust_level', 'good')  # excellent, good, poor
        repayment_notes = data.get('repayment_notes', '')
        
        if not lending_id:
            return jsonify({'error': 'Missing lending ID'}), 400
        
        # Convert trust level to numeric rating
        trust_level_map = {
            'excellent': 9,
            'good': 7,
            'poor': 3
        }
        
        if trust_level in trust_level_map:
            trust_rating = trust_level_map[trust_level]
        
        # Update lending transaction
        db = get_firestore_db()
        if db:
            lending_ref = db.collection(COLLECTIONS['user_lending']).document(lending_id)
            lending_doc = lending_ref.get()
            
            if not lending_doc.exists:
                return jsonify({'error': 'Lending transaction not found'}), 404
            
            lending_data = lending_doc.to_dict()
            if lending_data['lender_phone'] != phone:
                return jsonify({'error': 'Unauthorized'}), 403
            
            # Update status and add trust rating
            lending_ref.update({
                'status': 'repaid',
                'trust_rating': trust_rating,
                'trust_level': trust_level,
                'repayment_notes': repayment_notes,
                'repaid_at': datetime.now(timezone.utc)
            })
            
            # Update borrower's trust rating
            borrower_phone = lending_data['borrower_phone']
            update_borrower_trust_rating(borrower_phone, trust_rating, trust_level)
            
            return jsonify({
                'success': True,
                'message': f'Successfully marked as repaid with {trust_level} rating'
            })
        else:
            return jsonify({'error': 'Database connection failed'}), 500
            
    except Exception as e:
        logging.error(f"Error in repay_money: {e}")
        return jsonify({'error': 'Failed to update repayment status'}), 500

@app.route('/udhaar/lendings', methods=['GET'])
def get_lendings():
    """Get all lending transactions for the user"""
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        db = get_firestore_db()
        if db:
            # Get lendings where user is lender (simplified query to avoid index requirement)
            lender_query = db.collection(COLLECTIONS['user_lending'])\
                .where('lender_phone', '==', phone)
            
            lendings = []
            for doc in lender_query.stream():
                data = doc.to_dict()
                lendings.append({
                    'id': doc.id,
                    'borrower_name': data.get('borrower_name'),
                    'borrower_phone': data.get('borrower_phone'),
                    'amount': data.get('amount'),
                    'description': data.get('description'),
                    'due_date': data.get('due_date'),
                    'status': data.get('status'),
                    'trust_rating': data.get('trust_rating'),
                    'trust_level': data.get('trust_level'),
                    'created_at': data.get('created_at').isoformat() if data.get('created_at') else None,
                    'repaid_at': data.get('repaid_at').isoformat() if data.get('repaid_at') else None,
                    'voice_note_url': data.get('voice_note_url')
                })
            
            # Sort by created_at in descending order (client-side sorting)
            lendings.sort(key=lambda x: x['created_at'] or '', reverse=True)
            
            return jsonify({'lendings': lendings})
        else:
            return jsonify({'error': 'Database connection failed'}), 500
            
    except Exception as e:
        logging.error(f"Error in get_lendings: {e}")
        return jsonify({'error': 'Failed to fetch lendings'}), 500

@app.route('/udhaar/trust-rating/<borrower_phone>', methods=['GET'])
def get_trust_rating(borrower_phone):
    """Get trust rating for a specific borrower"""
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        db = get_firestore_db()
        if db:
            # Get trust rating from user_trust_ratings collection
            trust_query = db.collection(COLLECTIONS['user_trust_ratings'])\
                .where('borrower_phone', '==', borrower_phone)\
                .limit(1)
            
            trust_doc = None
            for doc in trust_query.stream():
                trust_doc = doc.to_dict()
                break
            
            if trust_doc:
                return jsonify({
                    'borrower_phone': borrower_phone,
                    'average_rating': trust_doc.get('average_rating', 0),
                    'total_transactions': trust_doc.get('total_transactions', 0),
                    'last_updated': trust_doc.get('last_updated').isoformat() if trust_doc.get('last_updated') else None
                })
            else:
                return jsonify({
                    'borrower_phone': borrower_phone,
                    'average_rating': 0,
                    'total_transactions': 0,
                    'last_updated': None
                })
        else:
            return jsonify({'error': 'Database connection failed'}), 500
            
    except Exception as e:
        logging.error(f"Error in get_trust_rating: {e}")
        return jsonify({'error': 'Failed to fetch trust rating'}), 500

@app.route('/udhaar/voice-upload', methods=['POST'])
def upload_voice_note():
    """Upload voice note for lending transaction"""
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        if 'voice_file' not in request.files:
            return jsonify({'error': 'No voice file provided'}), 400
        
        voice_file = request.files['voice_file']
        if voice_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"voice_notes/{phone}_{timestamp}_{voice_file.filename}"
        
        # Save to Firebase Storage (simplified - in real app, use Firebase Storage)
        # For now, we'll store the filename and simulate storage
        voice_url = f"/static/voice_notes/{filename}"
        
        return jsonify({
            'success': True,
            'voice_url': voice_url,
            'filename': filename
        })
        
    except Exception as e:
        logging.error(f"Error in upload_voice_note: {e}")
        return jsonify({'error': 'Failed to upload voice note'}), 500

def update_borrower_trust_rating(borrower_phone, new_rating, trust_level):
    """Update trust rating for a borrower"""
    try:
        db = get_firestore_db()
        if db:
            # Get existing trust rating
            trust_query = db.collection(COLLECTIONS['user_trust_ratings'])\
                .where('borrower_phone', '==', borrower_phone)\
                .limit(1)
            
            existing_doc = None
            for doc in trust_query.stream():
                existing_doc = doc
                break
            
            if existing_doc:
                # Update existing rating
                existing_data = existing_doc.to_dict()
                total_rating = existing_data.get('total_rating', 0) + new_rating
                total_transactions = existing_data.get('total_transactions', 0) + 1
                average_rating = total_rating / total_transactions
                
                # Update trust level based on average
                if average_rating >= 8:
                    overall_trust_level = 'excellent'
                elif average_rating >= 6:
                    overall_trust_level = 'good'
                else:
                    overall_trust_level = 'poor'
                
                existing_doc.reference.update({
                    'total_rating': total_rating,
                    'total_transactions': total_transactions,
                    'average_rating': average_rating,
                    'overall_trust_level': overall_trust_level,
                    'last_updated': datetime.now(timezone.utc)
                })
            else:
                # Create new trust rating
                overall_trust_level = 'excellent' if new_rating >= 8 else 'good' if new_rating >= 6 else 'poor'
                db.collection(COLLECTIONS['user_trust_ratings']).add({
                    'borrower_phone': borrower_phone,
                    'total_rating': new_rating,
                    'total_transactions': 1,
                    'average_rating': new_rating,
                    'overall_trust_level': overall_trust_level,
                    'created_at': datetime.now(timezone.utc),
                    'last_updated': datetime.now(timezone.utc)
                })
                
    except Exception as e:
        logging.error(f"Error updating trust rating: {e}")

@app.route('/udhaar/lending-analysis', methods=['POST'])
def analyze_lending_request():
    """Analyze lending request with comprehensive financial context"""
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        data = request.json
        borrower_phone = data.get('borrower_phone')
        requested_amount = data.get('amount')
        
        if not borrower_phone or not requested_amount:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get comprehensive financial data
        financial_analysis = perform_comprehensive_lending_analysis(phone, borrower_phone, requested_amount)
        
        return jsonify(financial_analysis)
        
    except Exception as e:
        logging.error(f"Error in lending analysis: {e}")
        return jsonify({'error': 'Failed to analyze lending request'}), 500

def perform_comprehensive_lending_analysis(phone: str, borrower_phone: str, requested_amount: float) -> Dict:
    """Perform comprehensive lending analysis with financial context"""
    
    # 1. Get user's financial data
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
    
    # 2. Get user's goals
    user_goals = get_user_goals(phone)
    
    # 3. Get cash assets
    cash_assets = get_user_cash_assets(phone)
    total_cash = sum(a['amount'] for a in cash_assets)
    
    # 4. Get upcoming transactions (next 15-20 days)
    upcoming_transactions = get_upcoming_transactions(user_data, days=20)
    
    # 5. Calculate financial metrics
    financial_metrics = calculate_lending_affordability_metrics(
        user_data, user_goals, total_cash, upcoming_transactions, requested_amount
    )
    
    # 6. Get borrower's trust rating
    trust_rating_response = requests.get(f"http://localhost:5001/udhaar/trust-rating/{borrower_phone}")
    trust_data = trust_rating_response.json() if trust_rating_response.status_code == 200 else {
        'average_rating': 0,
        'total_transactions': 0,
        'overall_trust_level': 'unknown'
    }
    
    # 7. Use custom agent for AI analysis
    try:
        agent_analysis = custom_agent.analyze_financial_query(
            user_message=f"Should I lend ₹{requested_amount:,.0f} to {borrower_phone}? My current cash is ₹{total_cash:,.0f} and I have upcoming expenses of ₹{upcoming_transactions['total_amount']:,.0f} in the next 20 days.",
            financial_data=user_data,
            user_profile={
                'goals': user_goals,
                'cash_assets': cash_assets,
                'upcoming_transactions': upcoming_transactions,
                'trust_rating': trust_data
            }
        )
    except Exception as e:
        logging.error(f"Agent analysis failed: {e}")
        agent_analysis = {
            'response': f"Based on your financial profile, I need to analyze if you can afford to lend ₹{requested_amount:,.0f}.",
            'analysis_type': 'lending_borrowing',
            'recommendations': []
        }
    
    # 8. Compile comprehensive analysis
    analysis_result = {
        'analysis_type': 'lending_affordability',
        'requested_amount': requested_amount,
        'borrower_phone': borrower_phone,
        'financial_metrics': financial_metrics,
        'trust_analysis': {
            'borrower_phone': borrower_phone,
            'average_rating': trust_data.get('average_rating', 0),
            'total_transactions': trust_data.get('total_transactions', 0),
            'overall_trust_level': trust_data.get('overall_trust_level', 'unknown'),
            'recommendation': get_lending_recommendation(trust_data, requested_amount)
        },
        'cash_analysis': {
            'total_cash_assets': total_cash,
            'cash_after_lending': total_cash - requested_amount,
            'cash_after_upcoming_expenses': total_cash - requested_amount - upcoming_transactions['total_amount']
        },
        'upcoming_transactions': upcoming_transactions,
        'goals_impact': analyze_goals_impact(user_goals, requested_amount),
        'agent_analysis': agent_analysis,
        'recommendation': generate_lending_recommendation(financial_metrics, trust_data, requested_amount)
    }
    
    return analysis_result

def get_upcoming_transactions(user_data: Dict, days: int = 20) -> Dict:
    """Extract upcoming transactions from financial data"""
    upcoming_transactions = []
    total_amount = 0
    
    try:
        # Check bank transactions for upcoming payments
        bank_transactions = user_data.get('fetch_bank_transactions', {}).get('bankTransactionsResponse', {}).get('transactions', [])
        
        # Look for recurring transactions (EMIs, subscriptions, etc.)
        current_date = datetime.now()
        end_date = current_date + timedelta(days=days)
        
        for transaction in bank_transactions:
            try:
                # Parse transaction date
                if isinstance(transaction, dict) and 'transactionDate' in transaction:
                    tx_date_str = transaction['transactionDate']
                    # Handle different date formats
                    if 'T' in tx_date_str:
                        tx_date = datetime.fromisoformat(tx_date_str.replace('Z', '+00:00'))
                    else:
                        tx_date = datetime.strptime(tx_date_str, '%Y-%m-%d')
                    
                    # Check if transaction is in the future within our window
                    if current_date <= tx_date <= end_date:
                        amount = abs(float(transaction.get('amount', 0)))
                        upcoming_transactions.append({
                            'date': tx_date.isoformat(),
                            'description': transaction.get('narration', 'Unknown'),
                            'amount': amount,
                            'type': 'upcoming_payment'
                        })
                        total_amount += amount
            except Exception as e:
                logging.warning(f"Error parsing transaction: {e}")
                continue
        
        # Add estimated recurring expenses
        estimated_expenses = [
            {'description': 'Estimated monthly bills', 'amount': 5000},
            {'description': 'Estimated groceries', 'amount': 3000},
            {'description': 'Estimated fuel/transport', 'amount': 2000}
        ]
        
        for expense in estimated_expenses:
            upcoming_transactions.append({
                'date': (current_date + timedelta(days=15)).isoformat(),
                'description': expense['description'],
                'amount': expense['amount'],
                'type': 'estimated_expense'
            })
            total_amount += expense['amount']
            
    except Exception as e:
        logging.error(f"Error extracting upcoming transactions: {e}")
    
    return {
        'transactions': upcoming_transactions,
        'total_amount': total_amount,
        'days_analyzed': days
    }

def calculate_lending_affordability_metrics(user_data: Dict, user_goals: List[Dict], 
                                         total_cash: float, upcoming_transactions: Dict, 
                                         requested_amount: float) -> Dict:
    """Calculate comprehensive affordability metrics"""
    
    # Extract portfolio data
    portfolio = user_data.get('fetch_net_worth', {}).get('netWorthResponse', {})
    net_worth = float(portfolio.get('totalNetWorthValue', {}).get('units', 0)) if portfolio else 0
    
    # Calculate upcoming expenses
    upcoming_total = upcoming_transactions['total_amount']
    
    # Calculate goals funding requirements
    goals_funding_needed = 0
    for goal in user_goals:
        goal_amount = float(goal.get('amount', 0))
        goal_year = int(goal.get('year', 1))
        monthly_goal_savings = goal_amount / (goal_year * 12)
        goals_funding_needed += monthly_goal_savings
    
    # Calculate affordability metrics
    cash_after_lending = total_cash - requested_amount
    cash_after_expenses = cash_after_lending - upcoming_total
    emergency_fund_ratio = (cash_after_expenses / (upcoming_total * 3)) * 100 if upcoming_total > 0 else 100
    
    # Risk assessment
    risk_level = 'low'
    if cash_after_expenses < 0:
        risk_level = 'high'
    elif cash_after_expenses < (upcoming_total * 2):
        risk_level = 'medium'
    
    return {
        'net_worth': net_worth,
        'total_cash': total_cash,
        'cash_after_lending': cash_after_lending,
        'cash_after_expenses': cash_after_expenses,
        'upcoming_expenses': upcoming_total,
        'goals_funding_needed': goals_funding_needed,
        'emergency_fund_ratio': emergency_fund_ratio,
        'risk_level': risk_level,
        'affordability_score': calculate_affordability_score(cash_after_expenses, requested_amount, net_worth)
    }

def calculate_affordability_score(cash_after_expenses: float, requested_amount: float, net_worth: float) -> float:
    """Calculate affordability score (0-100)"""
    if cash_after_expenses < 0:
        return 0  # Cannot afford
    
    # Base score on remaining cash
    cash_score = min(100, (cash_after_expenses / requested_amount) * 50)
    
    # Adjust based on net worth ratio
    net_worth_ratio = requested_amount / net_worth if net_worth > 0 else 1
    net_worth_score = max(0, 50 - (net_worth_ratio * 25))
    
    return min(100, cash_score + net_worth_score)

def analyze_goals_impact(user_goals: List[Dict], requested_amount: float) -> Dict:
    """Analyze how lending will impact user's goals"""
    total_goals_amount = sum(float(goal.get('amount', 0)) for goal in user_goals)
    goals_impact_ratio = (requested_amount / total_goals_amount * 100) if total_goals_amount > 0 else 0
    
    impacted_goals = []
    for goal in user_goals:
        goal_amount = float(goal.get('amount', 0))
        impact_percentage = (requested_amount / goal_amount * 100) if goal_amount > 0 else 0
        if impact_percentage > 10:  # Goals with >10% impact
            impacted_goals.append({
                'goal_name': goal.get('name', 'Unknown'),
                'goal_amount': goal_amount,
                'impact_percentage': impact_percentage
            })
    
    return {
        'total_goals_amount': total_goals_amount,
        'lending_impact_ratio': goals_impact_ratio,
        'impacted_goals': impacted_goals,
        'will_delay_goals': goals_impact_ratio > 20
    }

def generate_lending_recommendation(financial_metrics: Dict, trust_data: Dict, requested_amount: float) -> Dict:
    """Generate comprehensive lending recommendation"""
    
    affordability_score = financial_metrics['affordability_score']
    risk_level = financial_metrics['risk_level']
    trust_level = trust_data.get('overall_trust_level', 'unknown')
    
    # Determine recommendation
    if affordability_score >= 80 and trust_level in ['excellent', 'good']:
        recommendation = 'APPROVE'
        reason = 'Strong financial position and good trust rating'
    elif affordability_score >= 60 and trust_level == 'excellent':
        recommendation = 'APPROVE_WITH_CAUTION'
        reason = 'Moderate financial position but excellent trust rating'
    elif affordability_score >= 70 and trust_level == 'good':
        recommendation = 'APPROVE_WITH_CAUTION'
        reason = 'Good financial position but moderate trust rating'
    elif affordability_score < 50:
        recommendation = 'REJECT'
        reason = 'Insufficient financial capacity'
    else:
        recommendation = 'REJECT'
        reason = 'Poor trust rating or financial constraints'
    
    return {
        'recommendation': recommendation,
        'reason': reason,
        'affordability_score': affordability_score,
        'risk_level': risk_level,
        'trust_level': trust_level,
        'suggested_amount': min(requested_amount, financial_metrics['cash_after_expenses'] * 0.8) if financial_metrics['cash_after_expenses'] > 0 else 0
    }

@app.route('/adk/info', methods=['GET'])
def get_adk_info():
    """Get ADK agent information"""
    try:
        adk_info = custom_agent.get_adk_info()
        return jsonify(adk_info)
    except Exception as e:
        logging.error(f"Error getting ADK info: {e}")
        return jsonify({'error': 'Failed to get ADK info'}), 500

@app.route('/adk/compliance', methods=['GET'])
def check_adk_compliance():
    """Check ADK compliance"""
    try:
        compliance = custom_agent.validate_adk_compliance()
        return jsonify(compliance)
    except Exception as e:
        logging.error(f"Error checking ADK compliance: {e}")
        return jsonify({'error': 'Failed to check ADK compliance'}), 500

@app.route('/adk/tools', methods=['GET'])
def get_adk_tools():
    """Get ADK tool definitions"""
    try:
        tools = custom_agent.get_tools()
        return jsonify({'tools': tools})
    except Exception as e:
        logging.error(f"Error getting ADK tools: {e}")
        return jsonify({'error': 'Failed to get ADK tools'}), 500

@app.route('/adk/schema', methods=['GET'])
def get_adk_schema():
    """Get ADK response schema"""
    try:
        schema = custom_agent.get_schema()
        return jsonify({'schema': schema})
    except Exception as e:
        logging.error(f"Error getting ADK schema: {e}")
        return jsonify({'error': 'Failed to get ADK schema'}), 500

@app.route('/adk/function-call', methods=['POST'])
def adk_function_call():
    """Execute ADK function call"""
    try:
        data = request.json
        function_name = data.get('function_name')
        args = data.get('args', {})
        
        if not function_name:
            return jsonify({'error': 'Missing function_name'}), 400
        
        result = custom_agent.call_function(function_name, args)
        return jsonify({
            'function_name': function_name,
            'result': result,
            'success': 'error' not in result
        })
    except Exception as e:
        logging.error(f"Error in ADK function call: {e}")
        return jsonify({'error': 'Failed to execute function call'}), 500

@app.route('/adk/analyze', methods=['POST'])
def adk_analyze():
    """ADK-compliant analysis endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '')
        financial_data = data.get('financial_data', {})
        chat_history = data.get('chat_history', [])
        user_profile = data.get('user_profile', {})
        
        if not user_message:
            return jsonify({'error': 'Missing message'}), 400
        
        # Use ADK-compliant analysis
        result = custom_agent.analyze_financial_query_adk(
            user_message, financial_data, chat_history, user_profile
        )
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in ADK analysis: {e}")
        return jsonify({'error': 'Failed to perform ADK analysis'}), 500

@app.route('/test-fi-mcp', methods=['GET'])
def test_fi_mcp_connection():
    """
    Test endpoint to verify fi-mcp server connectivity
    """
    phone = session.get('phone', '9611133087')  # Default test phone
    
    try:
        # Test basic connectivity
        response = requests.get("http://localhost:8484/", timeout=5)
        connectivity_status = "Connected" if response.status_code < 500 else f"Error: {response.status_code}"
    except Exception as e:
        connectivity_status = f"Not connected: {str(e)}"
    
    # Test data fetching
    test_data = {}
    data_types = ['bank_transactions', 'net_worth']
    
    for data_type in data_types:
        try:
            data = fetch_fi_mcp_data(phone, data_type)
            if data:
                # Handle different response formats
                if isinstance(data, dict):
                    test_data[data_type] = {
                        'status': 'Success',
                        'data_keys': list(data.keys())
                    }
                elif isinstance(data, list):
                    test_data[data_type] = {
                        'status': 'Success',
                        'data_keys': [f'item_{i}' for i in range(len(data))]
                    }
                else:
                    test_data[data_type] = {
                        'status': 'Success',
                        'data_keys': ['unknown_format']
                    }
            else:
                test_data[data_type] = {
                    'status': 'No data',
                    'data_keys': []
                }
        except Exception as e:
            test_data[data_type] = {
                'status': f'Error: {str(e)}',
                'data_keys': []
            }
    
    return jsonify({
        'fi_mcp_server': 'http://localhost:8484/mcp/stream',
        'connectivity': connectivity_status,
        'test_phone': phone,
        'test_results': test_data
    })

@app.route('/fi-mcp-auth', methods=['POST'])
def fi_mcp_auth():
    """
    Handle fi-mcp authentication flow
    """
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        # Generate a session ID for this user
        session_id = f"mcp-session-{str(uuid.uuid4())}"
        
        # Store the session ID in the user's session for future requests
        session['fi_mcp_session_id'] = session_id
        
        # Try to call a tool to trigger authentication
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "fetch_bank_transactions",
                "arguments": {}
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        }
        
        response = requests.post(
            FI_MCP_SERVER_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'content' in result['result']:
                content = result['result']['content']
                
                # Check if this is an authentication required response
                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]
                    if isinstance(first_item, dict) and 'text' in first_item:
                        try:
                            text_content = json.loads(first_item['text'])
                            if text_content.get('status') == 'login_required':
                                login_url = text_content.get('login_url')
                                return jsonify({
                                    'status': 'auth_required',
                                    'session_id': session_id,
                                    'login_url': login_url,
                                    'message': 'Please authenticate with fi-mcp server'
                                })
                        except json.JSONDecodeError:
                            pass
                
                # If we get actual data, authentication was successful
                return jsonify({
                    'status': 'authenticated',
                    'session_id': session_id,
                    'message': 'Successfully authenticated with fi-mcp server'
                })
        
        return jsonify({
            'status': 'error',
            'message': 'Failed to initiate authentication'
        }), 500
        
    except Exception as e:
        logging.error(f"Error in fi-mcp authentication: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/fi-mcp-retry', methods=['POST'])
def fi_mcp_retry():
    """
    Retry fi-mcp data fetch after authentication
    """
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    
    session_id = session.get('fi_mcp_session_id')
    if not session_id:
        return jsonify({'error': 'No session ID found'}), 400
    
    try:
        # Try to fetch data with the authenticated session
        user_data = {}
        data_types = ['bank_transactions', 'net_worth', 'credit_report', 'epf_details', 'insurance', 'mf_transactions', 'stock_transactions']
        
        for data_type in data_types:
            try:
                data = fetch_fi_mcp_data_with_session(phone, data_type, session_id)
                if data:
                    user_data[f'fetch_{data_type}'] = data
                else:
                    user_data[f'fetch_{data_type}'] = None
            except Exception as e:
                logging.error(f"Error fetching {data_type}: {e}")
                user_data[f'fetch_{data_type}'] = None
        
        # Check if we got any real data
        has_real_data = any(data is not None for data in user_data.values())
        
        if has_real_data:
            # Add cash assets to net worth
            cash_assets = get_user_cash_assets(phone)
            total_cash = sum(a['amount'] for a in cash_assets)
            
            # Patch net worth in response
            try:
                networth = user_data.get('fetch_net_worth', {}).get('netWorthResponse', {})
                if networth and 'totalNetWorthValue' in networth:
                    orig = float(networth['totalNetWorthValue']['units'])
                    networth['totalNetWorthValue']['units'] = orig + total_cash
                    if total_cash > 0:
                        networth['assetValues'].append({
                            'netWorthAttribute': 'ASSET_TYPE_CASH',
                            'value': {'currencyCode': 'INR', 'units': str(total_cash)}
                        })
            except Exception:
                pass
            
            user_data['cash_assets'] = cash_assets
            
            return jsonify({
                'status': 'success',
                'data': user_data,
                'message': 'Successfully fetched real data from fi-mcp server'
            })
        else:
            return jsonify({
                'status': 'no_data',
                'message': 'No real data available after authentication'
            })
        
    except Exception as e:
        logging.error(f"Error retrying fi-mcp data fetch: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def fetch_fi_mcp_data_with_session(phone: str, data_type: str, session_id: str) -> dict:
    """
    Fetch financial data from fi-mcp server using existing session
    """
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": f"fetch_{data_type}",
                "arguments": {}
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        }
        
        response = requests.post(
            FI_MCP_SERVER_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'content' in result['result']:
                content = result['result']['content']
                
                # Check if this is still an authentication required response
                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]
                    if isinstance(first_item, dict) and 'text' in first_item:
                        try:
                            text_content = json.loads(first_item['text'])
                            if text_content.get('status') == 'login_required':
                                logging.info(f"Still requires authentication for {data_type}")
                                return None
                        except json.JSONDecodeError:
                            pass
                
                # If we have actual data, parse it
                if isinstance(content, str):
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        logging.warning(f"Could not parse JSON content for {data_type}")
                        return None
                elif isinstance(content, dict):
                    return content
                else:
                    logging.warning(f"Unexpected content format for {data_type}: {type(content)}")
                    return None
            else:
                logging.warning(f"Unexpected fi-mcp response format for {data_type}: {result}")
                return None
        else:
            logging.error(f"fi-mcp server error for {data_type}: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error fetching {data_type} from fi-mcp: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error for {data_type}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error fetching {data_type}: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('FLASK_PORT', 5001))) 