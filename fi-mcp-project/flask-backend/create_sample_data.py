"""
Create sample data files for testing the context manager
"""

import json
import os
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample JSON files for testing"""
    
    # Sample reminders
    sample_reminders = [
        {
            "id": "rem_001",
            "title": "Pay credit card bill",
            "description": "Monthly credit card payment due",
            "date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "time": "09:00",
            "category": "payment",
            "status": "scheduled"
        },
        {
            "id": "rem_002", 
            "title": "Review investment portfolio",
            "description": "Monthly portfolio review and rebalancing",
            "date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
            "time": "10:00",
            "category": "investment",
            "status": "scheduled"
        },
        {
            "id": "rem_003",
            "title": "Old reminder",
            "description": "This should be filtered out",
            "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
            "time": "14:00",
            "category": "other",
            "status": "scheduled"
        }
    ]
    
    # Sample goals
    sample_goals = [
        {
            "id": "goal_001",
            "goal_name": "Emergency Fund",
            "target_amount": 25000,
            "current_amount": 15000,
            "target_date": "2025-12-31",
            "priority": "high",
            "category": "emergency_fund",
            "status": "active",
            "progress_percentage": 60.0
        },
        {
            "id": "goal_002",
            "goal_name": "House Down Payment", 
            "target_amount": 50000,
            "current_amount": 5000,
            "target_date": "2026-12-31",
            "priority": "high",
            "category": "house",
            "status": "active",
            "progress_percentage": 10.0
        },
        {
            "id": "goal_003",
            "goal_name": "Vacation Fund",
            "target_amount": 3000,
            "current_amount": 3000,
            "target_date": "2025-06-01",
            "priority": "low",
            "category": "vacation", 
            "status": "completed",
            "progress_percentage": 100.0
        }
    ]
    
    # Sample alerts
    sample_alerts = [
        {
            "id": "alert_001",
            "type": "price_target",
            "asset_symbol": "AAPL",
            "condition": "price above 200",
            "message": "Apple stock has reached target price",
            "status": "active"
        },
        {
            "id": "alert_002",
            "type": "portfolio_rebalance",
            "asset_symbol": "Portfolio",
            "condition": "portfolio weight deviation > 10%",
            "message": "Portfolio needs rebalancing",
            "status": "active"
        }
    ]
    
    # Write files
    files = {
        "user_reminders.json": sample_reminders,
        "user_goals.json": sample_goals,
        "user_alerts.json": sample_alerts
    }
    
    for filename, data in files.items():
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Created {filename}")

if __name__ == "__main__":
    create_sample_data()
    print("\n🎉 Sample data files created successfully!")
    print("You can now run: python3 gemini.py")