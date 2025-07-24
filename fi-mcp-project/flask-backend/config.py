import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for Gemini AI integration"""
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL: str = os.getenv('GEMINI_MODEL', 'gemini-2.5-pro')
    GEMINI_FLASH_MODEL: str = os.getenv('GEMINI_FLASH_MODEL', 'gemini-2.5-flash')
    
    # Default AI Instructions
    DEFAULT_SYSTEM_INSTRUCTION: str = os.getenv(
        'DEFAULT_SYSTEM_INSTRUCTION',
        'You are a professional financial advisor and wealth manager. Provide accurate, helpful, and personalized financial advice based on the user\'s data and questions. Always prioritize the user\'s financial well-being and provide actionable insights.'
    )
    
    # Flask Configuration
    FLASK_SECRET_KEY: str = os.getenv('FLASK_SECRET_KEY', 'your_secret_key_here')
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_PORT: int = int(os.getenv('FLASK_PORT', '5001'))
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required but not set in environment variables")
        return True
