"""
Tool definitions for Gemini AI function calling
This module contains all the function schemas/declarations for the AI tools
"""

from typing import Dict, List

class ToolDefinitions:
    """
    Centralized tool definitions for financial AI assistant
    """
    
    @staticmethod
    def get_schedule_reminder_tool() -> Dict:
        """Tool definition for scheduling reminders"""
        return {
            "name": "schedule_reminder",
            "description": "Schedules a financial reminder for the user at a specified date and time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the reminder (e.g., 'Pay credit card bill')",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of what needs to be done",
                    },
                    "date": {
                        "type": "string",
                        "description": "Date for the reminder (e.g., '2025-07-30')",
                    },
                    "time": {
                        "type": "string",
                        "description": "Time for the reminder (e.g., '09:00')",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["payment", "investment", "review", "tax", "insurance", "other"],
                        "description": "Category of the financial reminder",
                    },
                },
                "required": ["title", "date", "time", "category"],
            },
        }
    
    @staticmethod
    def get_generate_report_tool() -> Dict:
        """Tool definition for generating financial reports"""
        return {
            "name": "generate_financial_report",
            "description": "Generates a comprehensive financial analysis report based on user's data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["monthly", "quarterly", "annual", "custom"],
                        "description": "Type of financial report to generate",
                    },
                    "include_sections": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["net_worth", "cash_flow", "investments", "debt_analysis", "budget_variance", "recommendations"]
                        },
                        "description": "Sections to include in the report",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date for the report period (e.g., '2025-01-01')",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for the report period (e.g., '2025-07-30')",
                    },
                },
                "required": ["report_type", "include_sections"],
            },
        }
    
    @staticmethod
    def get_set_financial_goal_tool() -> Dict:
        """Tool definition for setting financial goals"""
        return {
            "name": "set_financial_goal",
            "description": "Sets a new financial goal for the user with tracking parameters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal_name": {
                        "type": "string",
                        "description": "Name of the financial goal (e.g., 'Emergency Fund', 'House Down Payment')",
                    },
                    "target_amount": {
                        "type": "number",
                        "description": "Target amount for the goal in currency",
                    },
                    "current_amount": {
                        "type": "number",
                        "description": "Current amount saved towards the goal",
                        "default": 0
                    },
                    "target_date": {
                        "type": "string",
                        "description": "Target date to achieve the goal (e.g., '2026-12-31')",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Priority level of the goal",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["emergency_fund", "retirement", "house", "education", "vacation", "debt_payoff", "other"],
                        "description": "Category of the financial goal",
                    },
                },
                "required": ["goal_name", "target_amount", "target_date", "priority", "category"],
            },
        }
    
    @staticmethod
    def get_create_investment_alert_tool() -> Dict:
        """Tool definition for creating investment alerts"""
        return {
            "name": "create_investment_alert",
            "description": "Creates an alert for investment opportunities or portfolio changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "alert_type": {
                        "type": "string",
                        "enum": ["price_target", "portfolio_rebalance", "dividend_date", "earnings_announcement", "custom"],
                        "description": "Type of investment alert",
                    },
                    "asset_symbol": {
                        "type": "string",
                        "description": "Stock symbol or asset identifier (e.g., 'AAPL', 'BTC')",
                    },
                    "condition": {
                        "type": "string",
                        "description": "Condition for the alert (e.g., 'price above 150', 'portfolio weight below 20%')",
                    },
                    "message": {
                        "type": "string",
                        "description": "Custom message for the alert",
                    },
                },
                "required": ["alert_type", "condition"],
            },
        }
    
    @classmethod
    def get_all_default_tools(cls) -> List[Dict]:
        """Get all default financial tools"""
        return [
            cls.get_schedule_reminder_tool(),
            cls.get_generate_report_tool(),
            cls.get_set_financial_goal_tool(),
            cls.get_create_investment_alert_tool()
        ]
    
    @classmethod
    def get_tool_by_name(cls, tool_name: str) -> Dict:
        """Get a specific tool definition by name"""
        tool_map = {
            "schedule_reminder": cls.get_schedule_reminder_tool(),
            "generate_financial_report": cls.get_generate_report_tool(),
            "set_financial_goal": cls.get_set_financial_goal_tool(),
            "create_investment_alert": cls.get_create_investment_alert_tool()
        }
        return tool_map.get(tool_name)
