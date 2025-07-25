from flask import Flask, request, jsonify, session, send_from_directory, abort
from flask_cors import CORS
import requests
import os
import json
import logging
from dotenv import load_dotenv
import re
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import desc

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key_here')
CORS(app, supports_credentials=True)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.0-pro')
GEMINI_FLASH_MODEL = os.environ.get('GEMINI_FLASH_MODEL', 'gemini-1.0-pro')
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
    total_cash = sum(a.amount for a in cash_assets)
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
    user_data['cash_assets'] = [
        {'id': a.id, 'amount': a.amount, 'description': a.description, 'timestamp': a.timestamp.isoformat()} for a in cash_assets
    ]
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

    gemini_payload = {
        "contents": [{"parts": [{"text": f"Give recommendations for: {user_data}"}]}]
    }
    try:
        gemini_resp = requests.post(GEMINI_API_URL, json=gemini_payload)
        if gemini_resp.status_code != 200:
            logging.error(f"Gemini API error: {gemini_resp.status_code} {gemini_resp.text}")
            return jsonify({"error": "Gemini API error", "details": gemini_resp.text}), 500
        return jsonify(gemini_resp.json())
    except Exception as e:
        logging.exception("Error calling Gemini API")
        return jsonify({"error": "Exception calling Gemini API", "details": str(e)}), 500

# Setup SQLAlchemy for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_insights.db'
db = SQLAlchemy(app)

class UserInsights(db.Model):
    phone = db.Column(db.String(32), primary_key=True)
    insights_json = db.Column(db.Text)
    last_updated = db.Column(db.DateTime)

def get_cached_insights(phone, max_age_minutes=1440):
    row = UserInsights.query.filter_by(phone=phone).first()
    if row and row.last_updated and (datetime.utcnow() - row.last_updated) < timedelta(minutes=max_age_minutes):
        try:
            return json.loads(row.insights_json)
        except Exception:
            return None
    return None

def set_cached_insights(phone, insights):
    row = UserInsights.query.filter_by(phone=phone).first()
    now = datetime.utcnow()
    if row:
        row.insights_json = json.dumps(insights)
        row.last_updated = now
    else:
        row = UserInsights(phone=phone, insights_json=json.dumps(insights), last_updated=now)
        db.session.add(row)
    db.session.commit()

class UserGoal(db.Model):
    phone = db.Column(db.String(32), primary_key=True)
    goals_json = db.Column(db.Text)
    last_updated = db.Column(db.DateTime)

def get_user_goals(phone):
    row = UserGoal.query.filter_by(phone=phone).first()
    if row and row.goals_json:
        try:
            return json.loads(row.goals_json)
        except Exception:
            return []
    return []

def set_user_goals(phone, goals):
    row = UserGoal.query.filter_by(phone=phone).first()
    now = datetime.utcnow()
    if row:
        row.goals_json = json.dumps(goals)
        row.last_updated = now
    else:
        row = UserGoal(phone=phone, goals_json=json.dumps(goals), last_updated=now)
        db.session.add(row)
    db.session.commit()

class UserChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(32), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(16))  # 'user' or 'assistant'
    text = db.Column(db.Text)

class UserHealthScore(db.Model):
    phone = db.Column(db.String(32), primary_key=True)
    health_score_json = db.Column(db.Text)
    last_updated = db.Column(db.DateTime)

class UserGoalInsights(db.Model):
    phone = db.Column(db.String(32), primary_key=True)
    goal_insights_json = db.Column(db.Text)
    last_updated = db.Column(db.DateTime)

def get_chat_history(phone, days=7):
    cutoff = datetime.utcnow() - timedelta(days=days)
    return UserChatHistory.query.filter_by(phone=phone).filter(UserChatHistory.timestamp >= cutoff).order_by(UserChatHistory.timestamp.asc()).all()

def add_chat_message(phone, role, text):
    # Clean up old messages for this user
    cutoff = datetime.utcnow() - timedelta(days=7)
    UserChatHistory.query.filter_by(phone=phone).filter(UserChatHistory.timestamp < cutoff).delete()
    # Add new message
    msg = UserChatHistory(phone=phone, role=role, text=text, timestamp=datetime.utcnow())
    db.session.add(msg)
    db.session.commit()

def get_cached_health_score(phone, max_age_minutes=1440):
    """Get cached health score if it exists and is not too old"""
    try:
        record = UserHealthScore.query.filter_by(phone=phone).first()
        if record and record.last_updated:
            age = datetime.utcnow() - record.last_updated
            if age.total_seconds() < max_age_minutes * 60:
                return json.loads(record.health_score_json)
    except Exception as e:
        logging.error(f"Error getting cached health score: {e}")
    return None

def set_cached_health_score(phone, health_score):
    """Cache health score in database"""
    try:
        record = UserHealthScore.query.filter_by(phone=phone).first()
        if record:
            record.health_score_json = json.dumps(health_score)
            record.last_updated = datetime.utcnow()
        else:
            record = UserHealthScore(
                phone=phone,
                health_score_json=json.dumps(health_score),
                last_updated=datetime.utcnow()
            )
            db.session.add(record)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error setting cached health score: {e}")
        db.session.rollback()

def get_cached_goal_insights(phone, max_age_minutes=1440):
    """Get cached goal-based insights if they exist and are not too old"""
    try:
        record = UserGoalInsights.query.filter_by(phone=phone).first()
        if record and record.last_updated:
            age = datetime.utcnow() - record.last_updated
            if age.total_seconds() < max_age_minutes * 60:
                return json.loads(record.goal_insights_json)
    except Exception as e:
        logging.error(f"Error getting cached goal insights: {e}")
    return None

def set_cached_goal_insights(phone, goal_insights):
    """Cache goal-based insights in database"""
    try:
        record = UserGoalInsights.query.filter_by(phone=phone).first()
        if record:
            record.goal_insights_json = json.dumps(goal_insights)
            record.last_updated = datetime.utcnow()
        else:
            record = UserGoalInsights(
                phone=phone,
                goal_insights_json=json.dumps(goal_insights),
                last_updated=datetime.utcnow()
            )
            db.session.add(record)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error setting cached goal insights: {e}")
        db.session.rollback()

class UserCashAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(32), index=True)
    amount = db.Column(db.Float)
    description = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class UserCashTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(32), index=True)
    amount = db.Column(db.Float)
    description = db.Column(db.String(256))
    type = db.Column(db.String(16))  # 'credit' or 'debit'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def get_user_cash_assets(phone):
    return UserCashAsset.query.filter_by(phone=phone).order_by(desc(UserCashAsset.timestamp)).all()

def add_user_cash_asset(phone, amount, description):
    asset = UserCashAsset(phone=phone, amount=amount, description=description)
    db.session.add(asset)
    db.session.commit()
    # Add as credit transaction
    txn = UserCashTransaction(phone=phone, amount=amount, description=description, type='credit')
    db.session.add(txn)
    db.session.commit()
    return asset

def delete_user_cash_asset(phone, asset_id):
    asset = UserCashAsset.query.filter_by(phone=phone, id=asset_id).first()
    if asset:
        db.session.delete(asset)
        db.session.commit()
        # Optionally, also delete the transaction
        UserCashTransaction.query.filter_by(phone=phone, amount=asset.amount, description=asset.description, type='credit').delete()
        db.session.commit()
        return True
    return False

@app.before_request
def create_tables():
    db.create_all()

@app.route('/goals', methods=['GET', 'POST'])
def user_goals():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401
    if request.method == 'GET':
        return jsonify({'goals': get_user_goals(phone)})
    if request.method == 'POST':
        try:
            goals = request.json.get('goals', [])
            set_user_goals(phone, goals)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': 'Failed to save goals', 'details': str(e)}), 400

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
            return jsonify({'insights': cached, 'cached': True})
    else:
        # Handle general insights caching
        cached = None if refresh else get_cached_insights(phone)
        if cached:
            return jsonify({'insights': cached, 'cached': True})

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
                return jsonify({"insights": insights, 'cached': False})
            except Exception as e:
                logging.error(f"Failed to parse Gemini insights JSON: {e}\nRaw text: {text}")
                return jsonify({"error": "Failed to parse Gemini insights JSON", "raw": text}), 500
        return jsonify({"error": "No candidates from Gemini", "raw": gemini_resp.json()}), 500
    except Exception as e:
        logging.exception("Error calling Gemini API for insights")
        return jsonify({"error": "Exception calling Gemini API", "details": str(e)}), 500

@app.route('/health-score', methods=['POST'])
def health_score():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    # Check for refresh parameter
    refresh = request.json.get('refresh', False) if request.is_json else False
    
    # Accept optional goals from frontend
    goals = request.json.get('goals') if request.is_json else None

    # Check cache first (unless refresh is requested)
    if not refresh:
        cached = get_cached_health_score(phone)
        if cached:
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
    if request.method == 'GET':
        assets = get_user_cash_assets(phone)
        return jsonify({'assets': [
            {'id': a.id, 'amount': a.amount, 'description': a.description, 'timestamp': a.timestamp.isoformat()} for a in assets
        ]})
    elif request.method == 'POST':
        data = request.json
        amount = float(data.get('amount', 0))
        description = data.get('description', '')
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        asset = add_user_cash_asset(phone, amount, description)
        return jsonify({'id': asset.id, 'amount': asset.amount, 'description': asset.description, 'timestamp': asset.timestamp.isoformat()})
    elif request.method == 'DELETE':
        asset_id = request.json.get('id')
        if not asset_id:
            return jsonify({'error': 'Asset id required'}), 400
        success = delete_user_cash_asset(phone, asset_id)
        return jsonify({'success': success})

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

@app.route('/chat-history', methods=['GET'])
def get_chat_history_endpoint():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        # Get last 7 days chat history from DB
        chat_history_db = get_chat_history(phone, days=7)
        chat_history = [{'role': msg.role, 'text': msg.text} for msg in chat_history_db]
        return jsonify({'history': chat_history})
    except Exception as e:
        logging.error(f"Error getting chat history: {e}")
        return jsonify({'error': 'Failed to load chat history'}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

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

    # Get last 7 days chat history from DB
    chat_history_db = get_chat_history(phone, days=7)
    chat_history = [{'role': msg.role, 'text': msg.text} for msg in chat_history_db]
    # Add the new user message to the history for prompt
    chat_history.append({'role': 'user', 'text': user_message})

    prefix = "Act as a financial advisor or wealth manager while looking into given data."
    history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['text']}" for msg in chat_history])
    prompt = f"{prefix}\nUser financial data: {user_data}\n{history_text}"
    gemini_payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        gemini_resp = requests.post(GEMINI_API_URL, json=gemini_payload)
        if gemini_resp.status_code != 200:
            logging.error(f"Gemini API error: {gemini_resp.status_code} {gemini_resp.text}")
            return jsonify({"error": "Gemini API error", "details": gemini_resp.text}), 500
        gemini_text = gemini_resp.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', str(gemini_resp.json()))
        # Store user and assistant messages in DB
        add_chat_message(phone, 'user', user_message)
        add_chat_message(phone, 'assistant', gemini_text)
        # Return last 7 days history (including the new ones)
        chat_history_db = get_chat_history(phone, days=7)
        chat_history = [{'role': msg.role, 'text': msg.text} for msg in chat_history_db]
        return jsonify({"response": gemini_text, "history": chat_history})
    except Exception as e:
        logging.exception("Error calling Gemini API")
        return jsonify({"error": "Exception calling Gemini API", "details": str(e)}), 500

@app.route('/news', methods=['GET'])
def personalised_news():
    phone = session.get('phone')
    if not phone:
        return jsonify({'error': 'Not logged in'}), 401

    # Gather user's investment data
    user_data = {}
    for endpoint in ['fetch_mf_transactions', 'fetch_stock_transactions', 'fetch_net_worth']:
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
                cleaned_text = text.strip()
                if cleaned_text.startswith('```'):
                    cleaned_text = re.sub(r'^```[a-zA-Z]*\s*', '', cleaned_text)
                    cleaned_text = re.sub(r'```$', '', cleaned_text)
                    cleaned_text = cleaned_text.strip()
                news_items = json.loads(cleaned_text)
                return jsonify({"news": news_items})
            except Exception as e:
                logging.error(f"Failed to parse Gemini news JSON: {e}\nRaw text: {text}")
                return jsonify({"error": "Failed to parse Gemini news JSON", "raw": text}), 500
        return jsonify({"error": "No candidates from Gemini", "raw": gemini_resp.json()}), 500
    except Exception as e:
        logging.exception("Error calling Gemini API for news")
        return jsonify({"error": "Exception calling Gemini API", "details": str(e)}), 500

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(port=port, debug=debug) 