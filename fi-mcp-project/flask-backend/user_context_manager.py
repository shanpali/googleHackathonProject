"""
User Context Manager for Gemini AI Integration
Handles loading and formatting existing user data for AI context
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class UserContextManager:
    """
    Manages user context data for AI interactions
    Loads existing reminders, goals, alerts, and other user data
    """
    
    def __init__(self, base_data_dir: str = "."):
        """
        Initialize the context manager
        
        Args:
            base_data_dir: Base directory for user data files
        """
        self.base_data_dir = base_data_dir
    
    def _load_json_file(self, filename: str) -> List[Dict]:
        """Load a JSON file and return its contents"""
        try:
            filepath = os.path.join(self.base_data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.warning(f"Could not load {filename}: {str(e)}")
            return []
    
    def get_user_reminders(self, phone: str = None) -> List[Dict]:
        """Get all active reminders for the user"""
        reminders = self._load_json_file("user_reminders.json")
        
        # Filter active reminders (you might want to add user-specific filtering)
        active_reminders = []
        for r in reminders:
            if r.get("status") == "scheduled":
                try:
                    # Parse the date string and compare with today's date
                    reminder_date = datetime.fromisoformat(r.get("date", "1900-01-01")).date()
                    if reminder_date >= datetime.now().date():
                        active_reminders.append(r)
                except ValueError:
                    # If date parsing fails, skip this reminder
                    logger.warning(f"Invalid date format in reminder: {r.get('date')}")
                    continue
        
        return active_reminders
    
    def get_user_goals(self, phone: str = None) -> List[Dict]:
        """Get all active financial goals for the user"""
        goals = self._load_json_file("user_goals.json")
        
        # Filter active goals and calculate progress
        active_goals = []
        for g in goals:
            if g.get("status") == "active":
                # Calculate progress percentage if not already present
                if "progress_percentage" not in g:
                    current = g.get("current_amount", 0)
                    target = g.get("target_amount", 1)  # Avoid division by zero
                    g["progress_percentage"] = (current / target) * 100 if target > 0 else 0
                active_goals.append(g)
        
        return active_goals
    
    def get_user_alerts(self, phone: str = None) -> List[Dict]:
        """Get all active investment alerts for the user"""
        alerts = self._load_json_file("user_alerts.json")
        
        # Filter active alerts
        active_alerts = [
            a for a in alerts 
            if a.get("status") == "active"
        ]
        
        return active_alerts
    
    def get_user_reports(self, phone: str = None) -> List[Dict]:
        """Get recent financial reports for the user"""
        # This would typically come from a database
        # For now, return mock data or implement file-based storage
        return []
    
    def format_user_context(
        self, 
        phone: str = None,
        include_financial_data: bool = True,
        financial_data: Optional[Dict] = None
    ) -> str:
        """
        Format comprehensive user context for AI
        
        Args:
            phone: User's phone number (for user-specific data)
            include_financial_data: Whether to include financial account data
            financial_data: Pre-loaded financial data
            
        Returns:
            Formatted context string for AI
        """
        context_parts = []
        
        # Get existing user app data
        reminders = self.get_user_reminders(phone)
        goals = self.get_user_goals(phone)
        alerts = self.get_user_alerts(phone)
        reports = self.get_user_reports(phone)
        
        # Format reminders context
        if reminders:
            reminder_text = "EXISTING REMINDERS:\n"
            for reminder in reminders:
                reminder_text += f"- {reminder.get('title')} on {reminder.get('date')} at {reminder.get('time')} ({reminder.get('category')})\n"
            context_parts.append(reminder_text)
        else:
            context_parts.append("EXISTING REMINDERS: None set")
        
        # Format goals context
        if goals:
            goals_text = "EXISTING FINANCIAL GOALS:\n"
            for goal in goals:
                progress = goal.get('progress_percentage', 0)
                goals_text += f"- {goal.get('goal_name')}: ${goal.get('current_amount', 0):,.0f} / ${goal.get('target_amount', 0):,.0f} ({progress:.1f}%) - Target: {goal.get('target_date')} (Priority: {goal.get('priority')})\n"
            context_parts.append(goals_text)
        else:
            context_parts.append("EXISTING FINANCIAL GOALS: None set")
        
        # Format alerts context
        if alerts:
            alerts_text = "EXISTING INVESTMENT ALERTS:\n"
            for alert in alerts:
                symbol = alert.get('asset_symbol', 'Portfolio')
                alerts_text += f"- {alert.get('type')} for {symbol}: {alert.get('condition')}\n"
            context_parts.append(alerts_text)
        else:
            context_parts.append("EXISTING INVESTMENT ALERTS: None set")
        
        # Add financial data if provided
        if include_financial_data and financial_data:
            context_parts.append(f"CURRENT FINANCIAL DATA:\n{self._format_financial_data(financial_data)}")
        
        # Add current date context
        context_parts.append(f"CURRENT DATE: {datetime.now().strftime('%Y-%m-%d')}")
        
        return "\n\n".join(context_parts)
    
    def _format_financial_data(self, financial_data: Dict) -> str:
        """Format financial data for AI context"""
        formatted_parts = []
        
        for data_type, data in financial_data.items():
            if data and isinstance(data, dict):
                if data_type == "fetch_net_worth":
                    if "total_assets" in data:
                        formatted_parts.append(f"Net Worth: ${data.get('total_assets', 0):,.0f} assets, ${data.get('total_liabilities', 0):,.0f} liabilities")
                
                elif data_type == "fetch_bank_transactions":
                    if "transactions" in data:
                        recent_count = len(data["transactions"][:5])  # Last 5 transactions
                        formatted_parts.append(f"Recent Bank Activity: {recent_count} recent transactions")
                
                elif data_type == "fetch_mf_transactions" or data_type == "fetch_stock_transactions":
                    if "holdings" in data:
                        holdings_count = len(data["holdings"])
                        formatted_parts.append(f"Investment Holdings ({data_type.replace('fetch_', '').replace('_transactions', '')}): {holdings_count} positions")
                
                elif data_type == "fetch_credit_report":
                    if "credit_score" in data:
                        formatted_parts.append(f"Credit Score: {data.get('credit_score', 'N/A')}")
        
        return "\n".join(formatted_parts) if formatted_parts else "Financial data available but not formatted"
    
    def get_contextual_prompt_enhancement(
        self, 
        base_prompt: str, 
        phone: str = None,
        financial_data: Optional[Dict] = None
    ) -> str:
        """
        Enhance a user prompt with relevant context
        
        Args:
            base_prompt: The original user prompt
            phone: User's phone number
            financial_data: User's financial data
            
        Returns:
            Enhanced prompt with context
        """
        user_context = self.format_user_context(
            phone=phone,
            financial_data=financial_data
        )
        
        enhanced_prompt = f"""USER CONTEXT:
{user_context}

USER REQUEST: {base_prompt}

Please consider the user's existing reminders, goals, and alerts when providing your response. 
Reference specific existing items when relevant, and avoid creating duplicates unless explicitly requested.
If setting new goals or reminders, consider how they relate to existing ones."""
        
        return enhanced_prompt

# Global instance
user_context_manager = UserContextManager()

def get_user_context_manager() -> UserContextManager:
    """Get the global user context manager instance"""
    return user_context_manager
