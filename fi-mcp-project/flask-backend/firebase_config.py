import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            # Create credentials from environment variables
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
                "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
                "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL')
            })
            
            # Initialize Firebase Admin SDK
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return False

def get_firestore_db():
    """Get Firestore database instance"""
    try:
        return firestore.client()
    except Exception as e:
        print(f"❌ Failed to get Firestore client: {e}")
        return None

# Firebase Collections
COLLECTIONS = {
    'user_insights': 'user_insights',
    'user_goals': 'user_goals', 
    'user_chat_history': 'user_chat_history',
    'user_health_score': 'user_health_score',
    'user_goal_insights': 'user_goal_insights',
    'user_cash_assets': 'user_cash_assets',
    'user_cash_transactions': 'user_cash_transactions',
    'user_news': 'user_news',
    'user_profiles': 'user_profiles',
    'user_lending': 'user_lending',
    'user_trust_ratings': 'user_trust_ratings',
    'user_voice_notes': 'user_voice_notes'
} 