"""
Implementation of financial tool functions
These are the actual functions called by the AI when using tools
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any
import logging
from tools import get_tool_registry

logger = logging.getLogger(__name__)

# Auto-register functions when module is imported
def auto_register_functions():
    """Automatically register all function implementations with the tool registry"""
    registry = get_tool_registry()
    
    # Register all the functions
    registry.register_function("schedule_reminder", schedule_reminder)
    registry.register_function("generate_financial_report", generate_financial_report)
    registry.register_function("set_financial_goal", set_financial_goal)
    registry.register_function("create_investment_alert", create_investment_alert)
    
    logger.info("Auto-registered all financial tool functions")

def schedule_reminder(title: str, date: str, time: str, category: str, description: str = "") -> Dict[str, Any]:
    """
    Schedule a financial reminder for the user
    
    Args:
        title: Title of the reminder
        date: Date for the reminder (YYYY-MM-DD format)
        time: Time for the reminder (HH:MM format)
        category: Category of the reminder
        description: Optional description
        
    Returns:
        Dict with reminder details and success status
    """
    try:
        # Create reminder object
        reminder = {
            "id": f"rem_{uuid.uuid4().hex[:8]}",
            "title": title,
            "description": description,
            "date": date,
            "time": time,
            "category": category,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        # Load existing reminders
        reminders_file = "user_reminders.json"
        existing_reminders = []
        
        if os.path.exists(reminders_file):
            with open(reminders_file, 'r') as f:
                existing_reminders = json.load(f)
        
        # Add new reminder
        existing_reminders.append(reminder)
        
        # Save back to file
        with open(reminders_file, 'w') as f:
            json.dump(existing_reminders, f, indent=2)
        
        return {
            "success": True,
            "reminder_id": reminder["id"],
            "message": f"Reminder '{title}' scheduled for {date} at {time}",
            "reminder": reminder
        }
        
    except Exception as e:
        logger.error(f"Error scheduling reminder: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def generate_financial_report(
    report_type: str, 
    include_sections: List[str], 
    start_date: str = None, 
    end_date: str = None
) -> Dict[str, Any]:
    """
    Generate a comprehensive financial report
    
    Args:
        report_type: Type of report (monthly, quarterly, annual, custom)
        include_sections: List of sections to include
        start_date: Start date for custom reports
        end_date: End date for custom reports
        
    Returns:
        Dict with report details and content
    """
    try:
        # Create report object
        report = {
            "id": f"report_{uuid.uuid4().hex[:8]}",
            "type": report_type,
            "sections": include_sections,
            "start_date": start_date,
            "end_date": end_date,
            "generated_at": datetime.now().isoformat(),
            "status": "generated"
        }
        
        # Generate mock report content based on sections
        content = {}
        for section in include_sections:
            if section == "net_worth":
                content[section] = {
                    "total_assets": 125000,
                    "total_liabilities": 45000,
                    "net_worth": 80000,
                    "change_from_last_period": "+5.2%"
                }
            elif section == "cash_flow":
                content[section] = {
                    "income": 8500,
                    "expenses": 6000,
                    "net_cash_flow": 2500,
                    "savings_rate": "29.4%"
                }
            elif section == "investments":
                content[section] = {
                    "total_value": 65000,
                    "ytd_return": "+12.3%",
                    "top_performers": ["VTSAX", "AAPL", "MSFT"]
                }
            # Add more sections as needed
        
        report["content"] = content
        
        return {
            "success": True,
            "report_id": report["id"],
            "message": f"{report_type.title()} financial report generated successfully",
            "report": report
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def set_financial_goal(
    goal_name: str,
    target_amount: float,
    target_date: str,
    priority: str,
    category: str,
    current_amount: float = 0
) -> Dict[str, Any]:
    """
    Set a new financial goal for the user
    
    Args:
        goal_name: Name of the goal
        target_amount: Target amount to achieve
        target_date: Target date (YYYY-MM-DD format)
        priority: Priority level (high, medium, low)
        category: Category of the goal
        current_amount: Current amount saved (default: 0)
        
    Returns:
        Dict with goal details and success status
    """
    try:
        # Create goal object
        goal = {
            "id": f"goal_{uuid.uuid4().hex[:8]}",
            "goal_name": goal_name,
            "target_amount": target_amount,
            "current_amount": current_amount,
            "target_date": target_date,
            "priority": priority,
            "category": category,
            "status": "active",
            "progress_percentage": (current_amount / target_amount) * 100 if target_amount > 0 else 0,
            "created_at": datetime.now().isoformat()
        }
        
        # Load existing goals
        goals_file = "user_goals.json"
        existing_goals = []
        
        if os.path.exists(goals_file):
            with open(goals_file, 'r') as f:
                existing_goals = json.load(f)
        
        # Add new goal
        existing_goals.append(goal)
        
        # Save back to file
        with open(goals_file, 'w') as f:
            json.dump(existing_goals, f, indent=2)
        
        return {
            "success": True,
            "goal_id": goal["id"],
            "message": f"Financial goal '{goal_name}' set with target of ${target_amount:,.2f} by {target_date}",
            "goal": goal
        }
        
    except Exception as e:
        logger.error(f"Error setting goal: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def create_investment_alert(
    alert_type: str,
    condition: str,
    asset_symbol: str = None,
    message: str = None
) -> Dict[str, Any]:
    """
    Create an investment alert
    
    Args:
        alert_type: Type of alert
        condition: Condition for triggering the alert
        asset_symbol: Optional asset symbol
        message: Optional custom message
        
    Returns:
        Dict with alert details and success status
    """
    try:
        # Create alert object
        alert = {
            "id": f"alert_{uuid.uuid4().hex[:8]}",
            "type": alert_type,
            "asset_symbol": asset_symbol or "Portfolio",
            "condition": condition,
            "message": message or f"Investment alert: {condition}",
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        # Load existing alerts
        alerts_file = "user_alerts.json"
        existing_alerts = []
        
        if os.path.exists(alerts_file):
            with open(alerts_file, 'r') as f:
                existing_alerts = json.load(f)
        
        # Add new alert
        existing_alerts.append(alert)
        
        # Save back to file
        with open(alerts_file, 'w') as f:
            json.dump(existing_alerts, f, indent=2)
        
        return {
            "success": True,
            "alert_id": alert["id"],
            "message": f"Investment alert created for {asset_symbol or 'Portfolio'}: {condition}",
            "alert": alert
        }
        
    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Auto-register functions when module is imported
auto_register_functions()
