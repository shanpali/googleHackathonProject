#!/usr/bin/env python3
"""
Firebase Setup Script for ArthaSetu AI Financial Dashboard
This script helps you set up Firebase for your hackathon project.
"""

import os
import json
from dotenv import load_dotenv

def print_banner():
    print("🔥" * 50)
    print("🔥 FIREBASE SETUP FOR ARTHASETU AI 🔥")
    print("🔥" * 50)
    print()

def print_instructions():
    print("📋 SETUP INSTRUCTIONS:")
    print("1. Go to https://console.firebase.google.com/")
    print("2. Create a new project (or use existing)")
    print("3. Enable Firestore Database")
    print("4. Go to Project Settings > Service Accounts")
    print("5. Generate new private key (JSON file)")
    print("6. Copy the values to your .env file")
    print()

def create_env_template():
    """Create a template .env file with Firebase configuration"""
    env_template = """# Gemini AI Configuration
GEMINI_API_KEY=<your-gemini-api-key>
GEMINI_MODEL=gemini-2.5-pro
GEMINI_FLASH_MODEL=gemini-2.5-flash

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
FLASK_PORT=5001

# Firebase Configuration (Google Cloud)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\nYour-Private-Key-Here\\n-----END PRIVATE KEY-----\\n"
FIREBASE_CLIENT_EMAIL=your-service-account-email@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email%40your-project.iam.gserviceaccount.com

# Default AI Instructions
DEFAULT_SYSTEM_INSTRUCTION=You are a professional financial advisor and wealth manager. Provide accurate, helpful, and personalized financial advice based on the user's data and questions. Always prioritize the user's financial well-being and provide actionable insights.
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("✅ Created .env.template file")
    print("📝 Copy the values from your Firebase service account JSON to .env file")

def extract_firebase_config():
    """Extract Firebase config from service account JSON"""
    print("🔧 FIREBASE CONFIG EXTRACTION:")
    print("If you have your Firebase service account JSON file:")
    
    json_path = input("Enter path to your service account JSON file (or press Enter to skip): ").strip()
    
    if json_path and os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                config = json.load(f)
            
            print("\n📋 Copy these values to your .env file:")
            print(f"FIREBASE_PROJECT_ID={config.get('project_id', 'your-project-id')}")
            print(f"FIREBASE_PRIVATE_KEY_ID={config.get('private_key_id', 'your-private-key-id')}")
            print(f"FIREBASE_PRIVATE_KEY=\"{config.get('private_key', 'your-private-key').replace(chr(10), '\\n')}\"")
            print(f"FIREBASE_CLIENT_EMAIL={config.get('client_email', 'your-service-account-email')}")
            print(f"FIREBASE_CLIENT_ID={config.get('client_id', 'your-client-id')}")
            print(f"FIREBASE_AUTH_URI={config.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth')}")
            print(f"FIREBASE_TOKEN_URI={config.get('token_uri', 'https://oauth2.googleapis.com/token')}")
            print(f"FIREBASE_AUTH_PROVIDER_X509_CERT_URL={config.get('auth_provider_x509_cert_url', 'https://www.googleapis.com/oauth2/v1/certs')}")
            print(f"FIREBASE_CLIENT_X509_CERT_URL={config.get('client_x509_cert_url', 'your-cert-url')}")
            
        except Exception as e:
            print(f"❌ Error reading JSON file: {e}")
    else:
        print("⏭️  Skipping JSON extraction")

def print_google_technologies():
    print("\n🚀 GOOGLE TECHNOLOGIES USED:")
    print("✅ Firebase Firestore (NoSQL Database)")
    print("✅ Firebase Authentication (User Management)")
    print("✅ Google Cloud Functions (Serverless)")
    print("✅ Gemini AI (Financial Advice)")
    print("✅ Google Cloud Storage (File Storage)")
    print("✅ Google Analytics (User Insights)")
    print()

def print_agentic_features():
    print("🤖 AGENTIC FEATURES ENABLED:")
    print("✅ Real-time data synchronization")
    print("✅ Multi-device user sessions")
    print("✅ Live notifications and alerts")
    print("✅ Collaborative financial planning")
    print("✅ AI-powered insights caching")
    print("✅ User behavior analytics")
    print("✅ Cloud-based data processing")
    print()

def main():
    print_banner()
    print_instructions()
    create_env_template()
    extract_firebase_config()
    print_google_technologies()
    print_agentic_features()
    
    print("🎯 NEXT STEPS:")
    print("1. Set up your Firebase project")
    print("2. Update your .env file with Firebase credentials")
    print("3. Run: pip install -r flask-backend/requirements.txt")
    print("4. Test Firebase connection")
    print("5. Deploy your hackathon project!")
    print()
    print("🔥 Good luck with your Google Hackathon! 🔥")

if __name__ == "__main__":
    main() 