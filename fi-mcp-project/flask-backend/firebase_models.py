from datetime import datetime, timezone, timedelta
import json
from firebase_config import get_firestore_db, COLLECTIONS

class FirebaseUserInsights:
    """Firebase model for user insights"""
    
    @staticmethod
    def get_cached_insights(phone, max_age_minutes=1440):
        """Get cached insights from Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return None
                
            doc_ref = db.collection(COLLECTIONS['user_insights']).document(phone)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                last_updated = data.get('last_updated')
                if last_updated:
                    # Convert Firestore timestamp to datetime
                    if hasattr(last_updated, 'timestamp'):
                        last_updated = datetime.fromtimestamp(last_updated.timestamp(), tz=timezone.utc)
                    
                    age = datetime.now(timezone.utc) - last_updated
                    if age.total_seconds() < max_age_minutes * 60:
                        return json.loads(data.get('insights_json', '{}'))
            return None
        except Exception as e:
            print(f"Error getting cached insights: {e}")
            return None
    
    @staticmethod
    def set_cached_insights(phone, insights):
        """Cache insights in Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return False
                
            doc_ref = db.collection(COLLECTIONS['user_insights']).document(phone)
            doc_ref.set({
                'phone': phone,
                'insights_json': json.dumps(insights),
                'last_updated': datetime.now(timezone.utc)
            })
            return True
        except Exception as e:
            print(f"Error setting cached insights: {e}")
            return False

class FirebaseUserGoals:
    """Firebase model for user goals"""
    
    @staticmethod
    def get_user_goals(phone):
        """Get user goals from Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return []
                
            doc_ref = db.collection(COLLECTIONS['user_goals']).document(phone)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                goals_json = data.get('goals_json')
                if goals_json:
                    return json.loads(goals_json)
            return []
        except Exception as e:
            print(f"Error getting user goals: {e}")
            return []
    
    @staticmethod
    def set_user_goals(phone, goals):
        """Set user goals in Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return False
                
            doc_ref = db.collection(COLLECTIONS['user_goals']).document(phone)
            doc_ref.set({
                'phone': phone,
                'goals_json': json.dumps(goals),
                'last_updated': datetime.now(timezone.utc)
            })
            return True
        except Exception as e:
            print(f"Error setting user goals: {e}")
            return False

class FirebaseUserChatHistory:
    """Firebase model for user chat history"""
    
    @staticmethod
    def get_chat_history(phone, days=7):
        """Get chat history from Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return []
            
            # Calculate cutoff date
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Query chat history for the user (simplified to avoid composite index)
            query = db.collection(COLLECTIONS['user_chat_history'])\
                     .where(field_path='phone', op_string='==', value=phone)
            
            messages = []
            for doc in query.stream():
                data = doc.to_dict()
                timestamp = data.get('timestamp')
                
                # Filter by timestamp in Python to avoid composite index
                if timestamp and timestamp >= cutoff:
                    messages.append({
                        'id': doc.id,
                        'phone': data.get('phone'),
                        'timestamp': timestamp,
                        'role': data.get('role'),
                        'text': data.get('text')
                    })
            
            # Sort in Python instead of Firestore
            messages.sort(key=lambda x: x['timestamp'])
            return messages
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
    
    @staticmethod
    def add_chat_message(phone, role, text):
        """Add chat message to Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return False
            
            # Clean up old messages (older than 7 days) - simplified query
            cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            old_messages_query = db.collection(COLLECTIONS['user_chat_history'])\
                                  .where(field_path='phone', op_string='==', value=phone)
            
            # Filter in Python to avoid composite index
            for doc in old_messages_query.stream():
                data = doc.to_dict()
                timestamp = data.get('timestamp')
                if timestamp and timestamp < cutoff:
                    doc.reference.delete()
            
            # Add new message
            db.collection(COLLECTIONS['user_chat_history']).add({
                'phone': phone,
                'role': role,
                'text': text,
                'timestamp': datetime.now(timezone.utc)
            })
            return True
        except Exception as e:
            print(f"Error adding chat message: {e}")
            return False

class FirebaseUserHealthScore:
    """Firebase model for user health score"""
    
    @staticmethod
    def get_cached_health_score(phone, max_age_minutes=1440):
        """Get cached health score from Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return None
                
            doc_ref = db.collection(COLLECTIONS['user_health_score']).document(phone)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                last_updated = data.get('last_updated')
                if last_updated:
                    if hasattr(last_updated, 'timestamp'):
                        last_updated = datetime.fromtimestamp(last_updated.timestamp(), tz=timezone.utc)
                    
                    age = datetime.now(timezone.utc) - last_updated
                    if age.total_seconds() < max_age_minutes * 60:
                        return json.loads(data.get('health_score_json', '{}'))
            return None
        except Exception as e:
            print(f"Error getting cached health score: {e}")
            return None
    
    @staticmethod
    def set_cached_health_score(phone, health_score):
        """Cache health score in Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return False
                
            doc_ref = db.collection(COLLECTIONS['user_health_score']).document(phone)
            doc_ref.set({
                'phone': phone,
                'health_score_json': json.dumps(health_score),
                'last_updated': datetime.now(timezone.utc)
            })
            return True
        except Exception as e:
            print(f"Error setting cached health score: {e}")
            return False

class FirebaseUserGoalInsights:
    """Firebase model for user goal insights"""
    
    @staticmethod
    def get_cached_goal_insights(phone, max_age_minutes=1440):
        """Get cached goal insights from Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return None
                
            doc_ref = db.collection(COLLECTIONS['user_goal_insights']).document(phone)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                last_updated = data.get('last_updated')
                if last_updated:
                    if hasattr(last_updated, 'timestamp'):
                        last_updated = datetime.fromtimestamp(last_updated.timestamp(), tz=timezone.utc)
                    
                    age = datetime.now(timezone.utc) - last_updated
                    if age.total_seconds() < max_age_minutes * 60:
                        return json.loads(data.get('goal_insights_json', '{}'))
            return None
        except Exception as e:
            print(f"Error getting cached goal insights: {e}")
            return None
    
    @staticmethod
    def set_cached_goal_insights(phone, goal_insights):
        """Cache goal insights in Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return False
                
            doc_ref = db.collection(COLLECTIONS['user_goal_insights']).document(phone)
            doc_ref.set({
                'phone': phone,
                'goal_insights_json': json.dumps(goal_insights),
                'last_updated': datetime.now(timezone.utc)
            })
            return True
        except Exception as e:
            print(f"Error setting cached goal insights: {e}")
            return False

class FirebaseUserProfile:
    """Firebase model for user profile"""
    
    @staticmethod
    def get_user_profile(phone):
        """Get user profile from Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return None
                
            doc_ref = db.collection(COLLECTIONS['user_profiles']).document(phone)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                # Convert to object-like structure
                class ProfileObject:
                    def __init__(self, data):
                        self.phone = data.get('phone', phone)
                        self.name = data.get('name', 'User')
                        self.email = data.get('email', '')
                        self.date_of_birth = data.get('date_of_birth')
                        self.occupation = data.get('occupation', '')
                        self.address = data.get('address', '')
                        self.emergency_contact = data.get('emergency_contact', '')
                        self.risk_profile = data.get('risk_profile', 'Moderate')
                        self.investment_goals = data.get('investment_goals', '')
                        self.created_at = data.get('created_at', datetime.now(timezone.utc))
                        self.updated_at = data.get('updated_at', datetime.now(timezone.utc))
                
                return ProfileObject(data)
            else:
                # Create default profile
                default_data = {
                    'phone': phone,
                    'name': 'User',
                    'email': '',
                    'date_of_birth': None,
                    'occupation': '',
                    'address': '',
                    'emergency_contact': '',
                    'risk_profile': 'Moderate',
                    'investment_goals': '',
                    'created_at': datetime.now(timezone.utc),
                    'updated_at': datetime.now(timezone.utc)
                }
                doc_ref.set(default_data)
                
                class ProfileObject:
                    def __init__(self, data):
                        self.phone = data.get('phone', phone)
                        self.name = data.get('name', 'User')
                        self.email = data.get('email', '')
                        self.date_of_birth = data.get('date_of_birth')
                        self.occupation = data.get('occupation', '')
                        self.address = data.get('address', '')
                        self.emergency_contact = data.get('emergency_contact', '')
                        self.risk_profile = data.get('risk_profile', 'Moderate')
                        self.investment_goals = data.get('investment_goals', '')
                        self.created_at = data.get('created_at', datetime.now(timezone.utc))
                        self.updated_at = data.get('updated_at', datetime.now(timezone.utc))
                
                return ProfileObject(default_data)
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    @staticmethod
    def update_user_profile(phone, profile_data):
        """Update user profile in Firestore"""
        try:
            db = get_firestore_db()
            if not db:
                return None
                
            doc_ref = db.collection(COLLECTIONS['user_profiles']).document(phone)
            
            # Get existing profile data
            existing_doc = doc_ref.get()
            existing_data = existing_doc.to_dict() if existing_doc.exists else {}
            
            # Merge with new data
            updated_data = {**existing_data, **profile_data}
            updated_data['phone'] = phone
            updated_data['updated_at'] = datetime.now(timezone.utc)
            
            # Set the updated data
            doc_ref.set(updated_data)
            
            # Return the updated profile object
            class ProfileObject:
                def __init__(self, data):
                    self.phone = data.get('phone', phone)
                    self.name = data.get('name', 'User')
                    self.email = data.get('email', '')
                    self.date_of_birth = data.get('date_of_birth')
                    self.occupation = data.get('occupation', '')
                    self.address = data.get('address', '')
                    self.emergency_contact = data.get('emergency_contact', '')
                    self.risk_profile = data.get('risk_profile', 'Moderate')
                    self.investment_goals = data.get('investment_goals', '')
                    self.created_at = data.get('created_at', datetime.now(timezone.utc))
                    self.updated_at = data.get('updated_at', datetime.now(timezone.utc))
            
            return ProfileObject(updated_data)
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return None

class FirebaseUserNews:
    """Firebase model for user news caching"""
    
    @staticmethod
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
    
    @staticmethod
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

class FirebaseUserCashTransaction:
    """Firebase model for user cash transactions"""
    @staticmethod
    def add_transaction(phone, amount, description, txn_type):
        try:
            db = get_firestore_db()
            if not db:
                return False
            db.collection(COLLECTIONS['user_cash_transactions']).add({
                'phone': phone,
                'amount': amount,
                'description': description,
                'type': txn_type,  # 'credit' or 'debit'
                'timestamp': datetime.now(timezone.utc)
            })
            return True
        except Exception as e:
            print(f"Error adding cash transaction: {e}")
            return False

    @staticmethod
    def get_transactions(phone, limit=100):
        try:
            db = get_firestore_db()
            if not db:
                return []
            query = db.collection(COLLECTIONS['user_cash_transactions'])\
                .where(field_path='phone', op_string='==', value=phone)
            txns = []
            for doc in query.stream():
                data = doc.to_dict()
                txns.append({
                    'id': doc.id,
                    'amount': data.get('amount'),
                    'description': data.get('description'),
                    'type': data.get('type'),
                    'timestamp': data.get('timestamp')
                })
            # Sort by timestamp descending
            txns.sort(key=lambda x: x['timestamp'], reverse=True)
            return txns[:limit]
        except Exception as e:
            print(f"Error fetching cash transactions: {e}")
            return []

    @staticmethod
    def delete_transaction(phone, txn_id):
        try:
            db = get_firestore_db()
            if not db:
                return False
            doc_ref = db.collection(COLLECTIONS['user_cash_transactions']).document(txn_id)
            doc = doc_ref.get()
            if doc.exists and doc.to_dict().get('phone') == phone:
                doc_ref.delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting cash transaction: {e}")
            return False 