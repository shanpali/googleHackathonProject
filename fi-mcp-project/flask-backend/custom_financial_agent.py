"""
Custom Financial Advisor Agent - ADK Compliant
Built specifically for fi-mcp-project hackathon
Advanced AI-powered financial analysis and recommendations with ADK framework
"""

import json
import logging
import requests
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CustomFinancialAgent:
    """
    Custom Financial Advisor Agent for fi-mcp-project - ADK Compliant
    Advanced AI-powered financial analysis with Indian context and ADK framework
    """
    
    def __init__(self):
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
        self.gemini_model = os.environ.get('GEMINI_MODEL', 'gemini-2.5-pro')
        self.gemini_api_url = f'https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}'
        
        # Agent capabilities and specializations
        self.capabilities = {
            'portfolio_analysis': True,
            'tax_optimization': True,
            'debt_management': True,
            'investment_planning': True,
            'risk_assessment': True,
            'goal_planning': True,
            'scenario_modeling': True,
            'cash_flow_analysis': True,
            'retirement_planning': True,
            'insurance_planning': True,
            'lending_analysis': True
        }
        
        # Indian financial context
        self.indian_context = {
            'tax_sections': ['80C', '80D', '80TTA', '80G', '80E'],
            'investment_options': ['ELSS', 'EPF', 'NPS', 'PPF', 'Mutual Funds', 'Stocks'],
            'insurance_products': ['Term Life', 'Health Insurance', 'ULIP', 'Endowment'],
            'debt_instruments': ['Personal Loan', 'Home Loan', 'Credit Card', 'Education Loan']
        }
        
        # ADK Tool Definitions
        self.tools = self._get_adk_tool_definitions()
        
        # Analysis frameworks
        self.analysis_frameworks = {
            'portfolio_optimization': self._portfolio_optimization_analysis,
            'tax_efficiency': self._tax_efficiency_analysis,
            'debt_management': self._debt_management_analysis,
            'investment_strategy': self._investment_strategy_analysis,
            'risk_assessment': self._risk_assessment_analysis,
            'goal_planning': self._goal_planning_analysis,
            'scenario_modeling': self._scenario_modeling_analysis,
            'cash_flow_analysis': self._cash_flow_analysis,
            'lending_borrowing': self._lending_borrowing_analysis
        }
        
        # ADK Response Schema
        self.response_schema = self._get_adk_response_schema()
        
        logging.info("🚀 ADK-Compliant Custom Financial Agent initialized successfully")
    
    def _get_adk_tool_definitions(self) -> List[Dict]:
        """Return ADK-compliant tool definitions"""
        return [
            {
                "name": "analyze_portfolio",
                "description": "Analyze portfolio allocation and performance with Indian context",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "portfolio_data": {
                            "type": "object",
                            "description": "User's portfolio data including investments, assets, and liabilities"
                        },
                        "risk_profile": {
                            "type": "string",
                            "enum": ["conservative", "moderate", "aggressive"],
                            "description": "User's risk tolerance profile"
                        },
                        "time_period": {
                            "type": "string",
                            "enum": ["1m", "3m", "6m", "1y", "3y", "5y"],
                            "description": "Analysis time period"
                        }
                    },
                    "required": ["portfolio_data"]
                }
            },
            {
                "name": "calculate_tax_savings",
                "description": "Calculate potential tax savings using Indian tax sections",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "income": {
                            "type": "number",
                            "description": "Annual income in INR"
                        },
                        "current_investments": {
                            "type": "object",
                            "description": "Current tax-saving investments"
                        },
                        "tax_sections": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tax sections to consider (80C, 80D, etc.)"
                        }
                    },
                    "required": ["income"]
                }
            },
            {
                "name": "assess_lending_affordability",
                "description": "Assess if user can afford to lend money considering financial context",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "requested_amount": {
                            "type": "number",
                            "description": "Amount to be lent in INR"
                        },
                        "borrower_trust_rating": {
                            "type": "object",
                            "description": "Borrower's trust rating and history"
                        },
                        "user_financial_data": {
                            "type": "object",
                            "description": "User's financial data including cash, goals, upcoming expenses"
                        }
                    },
                    "required": ["requested_amount", "user_financial_data"]
                }
            },
            {
                "name": "generate_goal_suggestions",
                "description": "Generate personalized financial goal suggestions based on user profile",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_profile": {
                            "type": "object",
                            "description": "User's financial profile and preferences"
                        },
                        "financial_data": {
                            "type": "object",
                            "description": "User's current financial data"
                        },
                        "goal_type": {
                            "type": "string",
                            "enum": ["short_term", "medium_term", "long_term"],
                            "description": "Type of goals to suggest"
                        }
                    },
                    "required": ["user_profile", "financial_data"]
                }
            },
            {
                "name": "calculate_health_score",
                "description": "Calculate comprehensive financial health score",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "financial_data": {
                            "type": "object",
                            "description": "User's financial data"
                        },
                        "user_goals": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "User's financial goals"
                        }
                    },
                    "required": ["financial_data"]
                }
            },
            {
                "name": "generate_insights",
                "description": "Generate personalized financial insights and alerts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "financial_data": {
                            "type": "object",
                            "description": "User's financial data"
                        },
                        "user_goals": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "User's financial goals"
                        },
                        "insight_type": {
                            "type": "string",
                            "enum": ["tax", "investment", "debt", "emergency", "all"],
                            "description": "Type of insights to generate"
                        }
                    },
                    "required": ["financial_data"]
                }
            }
        ]
    
    def _get_adk_response_schema(self) -> Dict:
        """Return ADK-compliant response schema"""
        return {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "Main analysis response text"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "Type of analysis performed"
                },
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "priority": {"type": "string"},
                            "description": {"type": "string"},
                            "action": {"type": "string"},
                            "save": {"type": "string"},
                            "icon": {"type": "string"}
                        }
                    }
                },
                "metrics": {
                    "type": "object",
                    "description": "Calculated financial metrics"
                },
                "tools_used": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tools used in analysis"
                },
                "confidence_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Confidence in the analysis"
                }
            },
            "required": ["response", "analysis_type"]
        }
    
    def get_tools(self) -> List[Dict]:
        """ADK-compliant method to get tool definitions"""
        return self.tools
    
    def get_schema(self) -> Dict:
        """ADK-compliant method to get response schema"""
        return self.response_schema
    
    def call_function(self, function_name: str, args: Dict) -> Dict:
        """ADK-compliant function calling"""
        try:
            if function_name == "analyze_portfolio":
                return self._call_analyze_portfolio(args)
            elif function_name == "calculate_tax_savings":
                return self._call_calculate_tax_savings(args)
            elif function_name == "assess_lending_affordability":
                return self._call_assess_lending_affordability(args)
            elif function_name == "generate_goal_suggestions":
                return self._call_generate_goal_suggestions(args)
            elif function_name == "calculate_health_score":
                return self._call_calculate_health_score(args)
            elif function_name == "generate_insights":
                return self._call_generate_insights(args)
            else:
                return {"error": f"Unknown function: {function_name}"}
        except Exception as e:
            logging.error(f"Error calling function {function_name}: {e}")
            return {"error": str(e)}
    
    def _call_analyze_portfolio(self, args: Dict) -> Dict:
        """ADK-compliant portfolio analysis"""
        portfolio_data = args.get('portfolio_data', {})
        risk_profile = args.get('risk_profile', 'moderate')
        time_period = args.get('time_period', '1y')
        
        # Use existing portfolio analysis
        analysis_result = self._portfolio_optimization_analysis(
            f"Analyze portfolio for {risk_profile} risk profile over {time_period}",
            {'portfolio': portfolio_data}
        )
        
        return {
            "analysis": analysis_result['text'],
            "recommendations": analysis_result.get('recommendations', []),
            "metrics": analysis_result.get('metrics', {}),
            "risk_profile": risk_profile,
            "time_period": time_period
        }
    
    def _call_calculate_tax_savings(self, args: Dict) -> Dict:
        """ADK-compliant tax savings calculation"""
        income = args.get('income', 0)
        current_investments = args.get('current_investments', {})
        tax_sections = args.get('tax_sections', ['80C', '80D'])
        
        # Use existing tax analysis
        analysis_result = self._tax_efficiency_analysis(
            f"Calculate tax savings for income ₹{income:,.0f} with sections {tax_sections}",
            {'income': income, 'investments': current_investments}
        )
        
        return {
            "tax_savings": analysis_result.get('tax_savings', 0),
            "recommendations": analysis_result.get('recommendations', []),
            "sections_analyzed": tax_sections,
            "analysis": analysis_result['text']
        }
    
    def _call_assess_lending_affordability(self, args: Dict) -> Dict:
        """ADK-compliant lending affordability assessment"""
        requested_amount = args.get('requested_amount', 0)
        borrower_trust_rating = args.get('borrower_trust_rating', {})
        user_financial_data = args.get('user_financial_data', {})
        
        # Use existing lending analysis
        analysis_result = self._lending_borrowing_analysis(
            f"Should I lend ₹{requested_amount:,.0f}?",
            {'portfolio': user_financial_data, 'profile': {'trust_rating': borrower_trust_rating}}
        )
        
        return {
            "affordability_score": analysis_result.get('metrics', {}).get('affordability_score', 0),
            "risk_level": analysis_result.get('metrics', {}).get('risk_level', 'unknown'),
            "recommendation": analysis_result.get('recommendation', 'unknown'),
            "analysis": analysis_result['text']
        }
    
    def _call_generate_goal_suggestions(self, args: Dict) -> Dict:
        """ADK-compliant goal suggestions generation"""
        user_profile = args.get('user_profile', {})
        financial_data = args.get('financial_data', {})
        goal_type = args.get('goal_type', 'medium_term')
        
        # Use existing goal planning
        analysis_result = self._goal_planning_analysis(
            f"Generate {goal_type} goal suggestions",
            {'portfolio': financial_data, 'profile': user_profile}
        )
        
        return {
            "suggestions": analysis_result.get('suggestions', []),
            "goal_type": goal_type,
            "analysis": analysis_result['text']
        }
    
    def _call_calculate_health_score(self, args: Dict) -> Dict:
        """ADK-compliant health score calculation"""
        financial_data = args.get('financial_data', {})
        user_goals = args.get('user_goals', [])
        
        # Use existing health score calculation
        health_score = self.calculate_health_score(financial_data, user_goals)
        
        return {
            "score": health_score.get('score', 0),
            "category": health_score.get('category', 'Unknown'),
            "breakdown": health_score.get('breakdown', {}),
            "recommendations": health_score.get('recommendations', [])
        }
    
    def _call_generate_insights(self, args: Dict) -> Dict:
        """ADK-compliant insights generation"""
        financial_data = args.get('financial_data', {})
        user_goals = args.get('user_goals', [])
        insight_type = args.get('insight_type', 'all')
        
        # Use existing insights generation
        insights = self.generate_insights(financial_data, user_goals)
        
        return {
            "insights": insights,
            "insight_type": insight_type,
            "total_insights": len(insights)
        }
    
    def analyze_financial_query_adk(self, user_message: str, financial_data: Dict, 
                                   chat_history: List[Dict] = None, user_profile: Dict = None) -> Dict:
        """
        ADK-compliant main entry point for financial analysis
        """
        logging.info("🎯 ADK Agent: Starting financial analysis")
        logging.info(f"📝 ADK Agent: User message: {user_message[:100]}...")
        
        try:
            # Analyze query intent
            intent_analysis = self._analyze_query_intent_custom(user_message)
            logging.info(f"🎯 ADK Agent: Intent detected: {intent_analysis['type']}")
            
            # Prepare financial context
            financial_context = self._prepare_comprehensive_context(financial_data, user_profile)
            
            # Determine which tools to use
            tools_to_use = self._determine_tools_to_use(intent_analysis, financial_context)
            
            # Execute tool calls
            tool_results = []
            for tool_name in tools_to_use:
                tool_args = self._prepare_tool_arguments(tool_name, financial_context, user_message)
                result = self.call_function(tool_name, tool_args)
                tool_results.append({
                    "tool": tool_name,
                    "result": result
                })
            
            # Route to analysis framework
            analysis_result = self._route_to_analysis_framework(
                intent_analysis['type'], 
                user_message, 
                financial_context, 
                chat_history
            )
            
            # Enhance response with ADK structure
            enhanced_response = self._enhance_response_with_adk_insights(analysis_result, financial_context, tool_results)
            
            # Validate against ADK schema
            final_response = self._validate_adk_response(enhanced_response)
            
            logging.info(f"✨ ADK Agent: Analysis complete - Tools used: {tools_to_use}")
            
            return final_response
            
        except Exception as e:
            logging.error(f"❌ ADK Agent: Error in analysis: {e}")
            return self._generate_adk_fallback_response(user_message, financial_data)
    
    def _determine_tools_to_use(self, intent_analysis: Dict, financial_context: Dict) -> List[str]:
        """Determine which ADK tools to use based on intent"""
        intent_type = intent_analysis['type']
        tools = []
        
        if intent_type == 'portfolio_analysis':
            tools.append('analyze_portfolio')
        elif intent_type == 'tax_optimization':
            tools.append('calculate_tax_savings')
        elif intent_type == 'lending_borrowing':
            tools.append('assess_lending_affordability')
        elif intent_type == 'goal_planning':
            tools.append('generate_goal_suggestions')
        
        # Always include health score and insights for comprehensive analysis
        tools.extend(['calculate_health_score', 'generate_insights'])
        
        return tools
    
    def _prepare_tool_arguments(self, tool_name: str, financial_context: Dict, user_message: str) -> Dict:
        """Prepare arguments for ADK tool calls"""
        if tool_name == 'analyze_portfolio':
            return {
                'portfolio_data': financial_context.get('portfolio', {}),
                'risk_profile': 'moderate',
                'time_period': '1y'
            }
        elif tool_name == 'calculate_tax_savings':
            return {
                'income': financial_context.get('income', 0),
                'current_investments': financial_context.get('investments', {}),
                'tax_sections': ['80C', '80D', '80TTA']
            }
        elif tool_name == 'assess_lending_affordability':
            return {
                'requested_amount': self._extract_amount_from_message(user_message),
                'borrower_trust_rating': financial_context.get('trust_rating', {}),
                'user_financial_data': financial_context
            }
        elif tool_name == 'generate_goal_suggestions':
            return {
                'user_profile': financial_context.get('profile', {}),
                'financial_data': financial_context.get('portfolio', {}),
                'goal_type': 'medium_term'
            }
        elif tool_name == 'calculate_health_score':
            return {
                'financial_data': financial_context.get('portfolio', {}),
                'user_goals': financial_context.get('goals', [])
            }
        elif tool_name == 'generate_insights':
            return {
                'financial_data': financial_context.get('portfolio', {}),
                'user_goals': financial_context.get('goals', []),
                'insight_type': 'all'
            }
        
        return {}
    
    def _extract_amount_from_message(self, message: str) -> float:
        """Extract amount from user message"""
        import re
        amount_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', message)
        if amount_match:
            return float(amount_match.group(1).replace(',', ''))
        return 0
    
    def _enhance_response_with_adk_insights(self, analysis_result: Dict, financial_context: Dict, tool_results: List[Dict]) -> Dict:
        """Enhance response with ADK tool results"""
        enhanced = analysis_result.copy()
        
        # Map analysis result to ADK response format
        if 'text' in enhanced:
            enhanced['response'] = enhanced.pop('text')
        
        if 'analysis_type' not in enhanced:
            enhanced['analysis_type'] = 'general'
        
        if 'recommendations' not in enhanced:
            enhanced['recommendations'] = []
        
        if 'metrics' not in enhanced:
            enhanced['metrics'] = {}
        
        # Add tool results
        enhanced['tools_used'] = [result['tool'] for result in tool_results]
        enhanced['tool_results'] = tool_results
        
        # Add confidence score
        enhanced['confidence_score'] = self._calculate_confidence_score(analysis_result, tool_results)
        
        # Add ADK-specific metadata
        enhanced['adk_version'] = '1.0'
        enhanced['agent_capabilities'] = list(self.capabilities.keys())
        
        return enhanced
    
    def _calculate_confidence_score(self, analysis_result: Dict, tool_results: List[Dict]) -> float:
        """Calculate confidence score for ADK response"""
        base_confidence = 0.7
        
        # Boost confidence if tools were used successfully
        if tool_results:
            base_confidence += 0.2
        
        # Boost confidence if recommendations are present
        if analysis_result.get('recommendations'):
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _validate_adk_response(self, response: Dict) -> Dict:
        """Validate response against ADK schema"""
        required_fields = self.response_schema.get('required', [])
        
        for field in required_fields:
            if field not in response:
                if field == 'response':
                    response[field] = "Analysis completed successfully."
                elif field == 'analysis_type':
                    response[field] = 'general'
                elif field == 'recommendations':
                    response[field] = []
                elif field == 'metrics':
                    response[field] = {}
                elif field == 'tools_used':
                    response[field] = []
                elif field == 'confidence_score':
                    response[field] = 0.5
                else:
                    response[field] = "Not available"
        
        return response
    
    def _generate_adk_fallback_response(self, user_message: str, financial_data: Dict) -> Dict:
        """Generate ADK-compliant fallback response"""
        return {
            "response": f"I'm having trouble analyzing your query: '{user_message}'. Please try rephrasing your question.",
            "analysis_type": "general",
            "recommendations": [],
            "metrics": {},
            "tools_used": [],
            "confidence_score": 0.1,
            "adk_version": "1.0",
            "agent_capabilities": list(self.capabilities.keys())
        }
    
    def _route_to_analysis_framework(self, analysis_type: str, user_message: str, 
                                   financial_context: Dict, chat_history: List[Dict] = None) -> Dict:
        """Route to appropriate analysis framework"""
        
        if analysis_type == 'portfolio_analysis':
            return self._portfolio_optimization_analysis(user_message, financial_context)
        elif analysis_type == 'tax_optimization':
            return self._tax_efficiency_analysis(user_message, financial_context)
        elif analysis_type == 'debt_management':
            return self._debt_management_analysis(user_message, financial_context)
        elif analysis_type == 'investment_planning':
            return self._investment_strategy_analysis(user_message, financial_context)
        elif analysis_type == 'risk_assessment':
            return self._risk_assessment_analysis(user_message, financial_context)
        elif analysis_type == 'goal_planning':
            return self._goal_planning_analysis(user_message, financial_context)
        elif analysis_type == 'scenario_modeling':
            return self._scenario_modeling_analysis(user_message, financial_context)
        elif analysis_type == 'cash_flow_analysis':
            return self._cash_flow_analysis(user_message, financial_context)
        elif analysis_type == 'salary_analysis':
            return self._salary_analysis(user_message, financial_context)
        elif analysis_type == 'lending_borrowing':
            return self._lending_borrowing_analysis(user_message, financial_context)
        else:
            return self._general_financial_analysis(user_message, financial_context)
    
    def _portfolio_optimization_analysis(self, user_message: str, financial_context: Dict) -> Dict:
        """Custom portfolio optimization analysis"""
        portfolio = financial_context.get('portfolio', {})
        metrics = financial_context.get('metrics', {})
        
        # Get user's actual financial data
        net_worth = portfolio.get('net_worth', 0)
        assets = portfolio.get('assets', [])
        liabilities = portfolio.get('liabilities', [])
        
        # Custom portfolio analysis logic
        analysis = {
            'text': f"Based on your portfolio analysis:\n\n",
            'recommendations': [],
            'insights': []
        }
        
        # Include user's actual net worth
        if net_worth > 0:
            analysis['text'] += f"• Your current net worth is ₹{net_worth:,.0f}\n"
        
        # Analyze asset allocation
        equity_exposure = sum(asset['value'] for asset in assets 
                            if 'equity' in asset.get('type', '').lower() or 
                               'stock' in asset.get('type', '').lower())
        total_assets = sum(asset['value'] for asset in assets)
        
        if total_assets > 0:
            equity_ratio = (equity_exposure / total_assets) * 100
            
            analysis['text'] += f"• Your equity exposure is {equity_ratio:.1f}% of your total assets (₹{equity_exposure:,.0f})\n"
            
            if equity_ratio < 30:
                analysis['text'] += "  - Consider increasing equity allocation for long-term growth\n"
                analysis['recommendations'].append("Increase equity exposure to 40-60%")
            elif equity_ratio > 70:
                analysis['text'] += "  - Consider adding debt instruments for stability\n"
                analysis['recommendations'].append("Add debt instruments for balance")
            else:
                analysis['text'] += "  - Your asset allocation appears well-balanced\n"
                analysis['recommendations'].append("Maintain current allocation")
        
        # Emergency fund analysis
        emergency_ratio = metrics.get('emergency_fund_ratio', 0)
        if emergency_ratio < 50:
            analysis['text'] += f"• Your emergency fund coverage is {emergency_ratio:.1f}% of recommended 6-month expenses\n"
            analysis['text'] += "  - Aim to build 3-6 months of expenses in emergency savings\n"
            analysis['recommendations'].append("Build emergency fund")
        else:
            analysis['text'] += f"• Your emergency fund coverage is {emergency_ratio:.1f}% - well maintained\n"
            analysis['insights'].append("Good emergency fund coverage")
        
        # Debt analysis
        total_debt = sum(liability['value'] for liability in liabilities)
        if total_debt > 0:
            debt_ratio = (total_debt / net_worth) * 100 if net_worth > 0 else 0
            analysis['text'] += f"• Your total debt is ₹{total_debt:,.0f} ({debt_ratio:.1f}% of net worth)\n"
            if debt_ratio > 30:
                analysis['text'] += "  - Consider debt reduction strategies\n"
                analysis['recommendations'].append("Prioritize debt reduction")
            else:
                analysis['text'] += "  - Your debt levels are manageable\n"
        
        analysis['text'] += "\nConsider diversifying across asset classes and rebalancing periodically."
        analysis['recommendations'].append("Rebalance portfolio quarterly")
        analysis['insights'].append("Portfolio optimization completed")
        
        return analysis
    
    def _tax_efficiency_analysis(self, user_message: str, financial_context: Dict) -> Dict:
        """Custom tax efficiency analysis"""
        analysis = {
            'text': "Tax Optimization Analysis:\n\n",
            'recommendations': [],
            'insights': []
        }
        
        # Section 80C optimization
        analysis['text'] += "• Maximize Section 80C deductions (₹1.5L limit):\n"
        analysis['text'] += "  - ELSS funds for equity exposure\n"
        analysis['text'] += "  - EPF for debt allocation\n"
        analysis['text'] += "  - Tax-saving FDs for stability\n\n"
        
        # Section 80D for health insurance
        analysis['text'] += "• Section 80D benefits:\n"
        analysis['text'] += "  - Health insurance premiums\n"
        analysis['text'] += "  - Preventive health check-ups\n\n"
        
        # Additional tax-saving opportunities
        analysis['text'] += "• Other tax-saving options:\n"
        analysis['text'] += "  - NPS for retirement planning\n"
        analysis['text'] += "  - Home loan interest deduction\n"
        analysis['text'] += "  - Education loan interest\n"
        
        analysis['recommendations'].extend([
            "Maximize Section 80C deductions",
            "Consider health insurance under 80D",
            "Explore NPS for additional deductions"
        ])
        
        analysis['insights'].extend([
            "Comprehensive tax optimization strategy",
            "Multiple deduction opportunities available"
        ])
        
        return analysis
    
    def _debt_management_analysis(self, user_message: str, financial_context: Dict) -> Dict:
        """Custom debt management analysis"""
        portfolio = financial_context.get('portfolio', {})
        liabilities = portfolio.get('liabilities', [])
        
        analysis = {
            'text': "Debt Management Analysis:\n\n",
            'recommendations': [],
            'insights': []
        }
        
        if liabilities:
            # Analyze debt structure
            high_interest_debts = [liab for liab in liabilities 
                                 if 'credit' in liab.get('type', '').lower() or 
                                    'personal' in liab.get('type', '').lower()]
            
            if high_interest_debts:
                analysis['text'] += "• Prioritize high-interest debts (credit cards, personal loans)\n"
                analysis['recommendations'].append("Pay off high-interest debts first")
            
            # Debt consolidation recommendation
            if len(liabilities) > 2:
                analysis['text'] += "• Consider debt consolidation for better interest rates\n"
                analysis['recommendations'].append("Explore debt consolidation")
            
            analysis['text'] += "• Maintain emergency fund before aggressive debt repayment\n"
            analysis['recommendations'].append("Maintain emergency fund")
            
        else:
            analysis['text'] += "• No outstanding debts detected. Good financial health!\n"
            analysis['insights'].append("Debt-free status maintained")
        
        analysis['text'] += "\nFocus on high-interest debts first while maintaining emergency savings."
        analysis['insights'].append("Debt management strategy optimized")
        
        return analysis
    
    def _investment_strategy_analysis(self, user_message: str, financial_context: Dict) -> Dict:
        """Custom investment strategy analysis"""
        portfolio = financial_context.get('portfolio', {})
        metrics = financial_context.get('metrics', {})
        
        # Get user's actual financial data
        net_worth = portfolio.get('net_worth', 0)
        assets = portfolio.get('assets', [])
        
        analysis = {
            'text': f"Investment Strategy Analysis:\n\n",
            'recommendations': [],
            'insights': []
        }
        
        # Include user's current investment position
        if net_worth > 0:
            analysis['text'] += f"• Your current net worth: ₹{net_worth:,.0f}\n"
        
        total_assets = sum(asset['value'] for asset in assets)
        if total_assets > 0:
            analysis['text'] += f"• Total investable assets: ₹{total_assets:,.0f}\n"
            
            # Analyze current asset allocation
            equity_assets = sum(asset['value'] for asset in assets 
                              if 'equity' in asset.get('type', '').lower() or 
                                 'stock' in asset.get('type', '').lower())
            debt_assets = sum(asset['value'] for asset in assets 
                            if 'debt' in asset.get('type', '').lower() or 
                               'bond' in asset.get('type', '').lower())
            
            equity_ratio = (equity_assets / total_assets) * 100 if total_assets > 0 else 0
            debt_ratio = (debt_assets / total_assets) * 100 if total_assets > 0 else 0
            
            analysis['text'] += f"• Current allocation: Equity {equity_ratio:.1f}%, Debt {debt_ratio:.1f}%\n"
        
        # Investment recommendations based on user's profile
        analysis['text'] += "\n• Recommended investment approach:\n"
        
        if net_worth > 1000000:  # High net worth
            analysis['text'] += "  - Consider diversified portfolio with international exposure\n"
            analysis['text'] += "  - Explore alternative investments (REITs, commodities)\n"
            analysis['recommendations'].append("Diversify internationally")
        elif net_worth > 500000:  # Medium net worth
            analysis['text'] += "  - Focus on balanced equity-debt allocation\n"
            analysis['text'] += "  - Consider tax-efficient investment options\n"
            analysis['recommendations'].append("Optimize tax efficiency")
        else:  # Growing net worth
            analysis['text'] += "  - Start with systematic investment plans (SIPs)\n"
            analysis['text'] += "  - Build emergency fund before aggressive investing\n"
            analysis['recommendations'].append("Start with SIPs")
        
        # SIP recommendations
        if net_worth > 0:
            suggested_sip = max(5000, net_worth * 0.01)  # 1% of net worth or ₹5,000
            analysis['text'] += f"  - Suggested monthly SIP: ₹{suggested_sip:,.0f}\n"
        
        analysis['recommendations'].extend([
            "Systematic Investment Plans (SIPs)",
            "Diversify across asset classes",
            "Regular portfolio rebalancing"
        ])
        
        analysis['insights'].extend([
            "Personalized investment strategy",
            "Risk-adjusted returns",
            "Long-term wealth creation"
        ])
        
        return analysis
    
    def _risk_assessment_analysis(self, user_message: str, financial_context: Dict) -> Dict:
        """Custom risk assessment analysis"""
        metrics = financial_context.get('metrics', {})
        
        analysis = {
            'text': "Risk Assessment Analysis:\n\n",
            'recommendations': [],
            'insights': []
        }
        
        # Emergency fund risk
        emergency_ratio = metrics.get('emergency_fund_ratio', 0)
        if emergency_ratio < 50:
            analysis['text'] += "• Emergency fund risk: HIGH\n"
            analysis['text'] += "  - Build 3-6 months of expenses\n"
            analysis['recommendations'].append("Build emergency fund immediately")
        else:
            analysis['text'] += "• Emergency fund: Adequate\n"
            analysis['insights'].append("Good emergency fund coverage")
        
        # Debt risk
        debt_ratio = metrics.get('debt_to_income_ratio', 0)
        if debt_ratio > 40:
            analysis['text'] += "• Debt risk: HIGH\n"
            analysis['text'] += "  - Focus on debt reduction\n"
            analysis['recommendations'].append("Prioritize debt reduction")
        else:
            analysis['text'] += "• Debt levels: Manageable\n"
            analysis['insights'].append("Healthy debt levels")
        
        # Investment risk
        investment_ratio = metrics.get('investment_ratio', 0)
        if investment_ratio < 20:
            analysis['text'] += "• Investment risk: LOW (under-invested)\n"
            analysis['recommendations'].append("Increase investment allocation")
        else:
            analysis['text'] += "• Investment allocation: Appropriate\n"
            analysis['insights'].append("Good investment allocation")
        
        analysis['text'] += "\nOverall risk profile assessment completed."
        analysis['insights'].append("Comprehensive risk analysis")
        
        return analysis
    
    def _goal_planning_analysis(self, user_message: str, financial_context: Dict) -> Dict:
        """Custom goal planning analysis with AI-generated suggestions"""
        logging.info(f"🎯 GOAL PLANNING: Starting analysis for: {user_message}")
        
        portfolio = financial_context.get('portfolio', {})
        metrics = financial_context.get('metrics', {})
        
        # Get user's actual financial data
        net_worth = portfolio.get('net_worth', 0)
        assets = portfolio.get('assets', [])
        
        logging.info(f"💰 GOAL PLANNING: User net worth: ₹{net_worth:,.0f}")
        logging.info(f"📊 GOAL PLANNING: Number of assets: {len(assets)}")
        
        # Generate AI-powered goal suggestions based on user message
        logging.info("🤖 GOAL PLANNING: Calling AI goal suggestions...")
        ai_suggestions = self._generate_ai_goal_suggestions(user_message, financial_context)
        logging.info(f"✅ GOAL PLANNING: AI suggestions generated: {len(ai_suggestions)} suggestions")
        
        analysis = {
            'text': f"Goal Planning Analysis for: {user_message}\n\n",
            'recommendations': [],
            'insights': [],
            'suggestions': ai_suggestions  # Include AI suggestions in the response
        }
        
        # Include user's current financial position
        if net_worth > 0:
            analysis['text'] += f"• Your current net worth: ₹{net_worth:,.0f}\n"
        
        # Analyze current asset allocation for goal planning
        total_assets = sum(asset['value'] for asset in assets)
        if total_assets > 0:
            analysis['text'] += f"• Total investable assets: ₹{total_assets:,.0f}\n"
        
        # Emergency fund analysis
        emergency_ratio = metrics.get('emergency_fund_ratio', 0)
        if emergency_ratio < 50:
            analysis['text'] += f"• Emergency fund coverage: {emergency_ratio:.1f}% (target: 100%)\n"
            analysis['text'] += "  - Priority: Build 3-6 months of expenses\n"
            analysis['recommendations'].append("Build emergency fund first")
        else:
            analysis['text'] += f"• Emergency fund coverage: {emergency_ratio:.1f}% - Good!\n"
        
        # Add AI-generated suggestions to the text
        if ai_suggestions:
            analysis['text'] += "\n• AI-Generated Goal Suggestions:\n"
            for i, suggestion in enumerate(ai_suggestions, 1):
                analysis['text'] += f"  {i}. {suggestion['name']}: ₹{suggestion['amount']:,.0f} by {suggestion['year']}\n"
                analysis['text'] += f"     Priority: {suggestion['priority']}\n"
                analysis['text'] += f"     Reasoning: {suggestion['reasoning']}\n"
                analysis['text'] += f"     Monthly savings needed: ₹{suggestion['monthly_savings_needed']:,.0f}\n\n"
                logging.info(f"🎯 GOAL PLANNING: Suggestion {i}: {suggestion['name']} - ₹{suggestion['amount']:,.0f}")
        
        # Goal-based recommendations
        if net_worth > 0:
            analysis['text'] += "\n• Goal-based planning strategy:\n"
            analysis['text'] += "  - Short-term (1-3 years): Focus on liquidity\n"
            analysis['text'] += "  - Medium-term (3-10 years): Balanced growth\n"
            analysis['text'] += "  - Long-term (10+ years): Equity-heavy portfolio\n"
            
            # Calculate potential retirement corpus
            monthly_expense_estimate = net_worth * 0.1 / 12  # Rough estimate
            retirement_corpus_needed = monthly_expense_estimate * 12 * 25  # 25 years
            analysis['text'] += f"  - Estimated retirement corpus needed: ₹{retirement_corpus_needed:,.0f}\n"
        
        analysis['recommendations'].extend([
            "Set specific financial goals",
            "Create emergency fund target",
            "Plan retirement corpus",
            "Diversify investments"
        ])
        
        analysis['insights'].extend([
            "Goal-oriented financial planning",
            "Emergency fund priority",
            "Long-term wealth building"
        ])
        
        logging.info(f"📋 GOAL PLANNING: Analysis completed - Text length: {len(analysis['text'])}, Recommendations: {len(analysis['recommendations'])}")
        logging.info(f"🎯 GOAL PLANNING: Final suggestions count: {len(analysis.get('suggestions', []))}")
        
        return analysis
    
    def _generate_ai_goal_suggestions(self, user_message: str, financial_context: Dict) -> List[Dict]:
        """Generate AI-powered goal suggestions based on user input and financial context"""
        logging.info(f"🤖 AI GOAL SUGGESTIONS: Starting for message: {user_message}")
        
        try:
            portfolio = financial_context.get('portfolio', {})
            metrics = financial_context.get('metrics', {})
            net_worth = portfolio.get('net_worth', 0)
            
            logging.info(f"💰 AI GOAL SUGGESTIONS: User net worth: ₹{net_worth:,.0f}")
            
            # Create a specialized prompt for goal generation
            goal_prompt = f"""
            As a financial advisor, create personalized goal suggestions based on the user's request.
            
            User request: "{user_message}"
            User's net worth: ₹{net_worth:,.0f}
            
            Generate 2-3 realistic and achievable financial goals in this exact JSON format:
            {{
                "suggestions": [
                    {{
                        "name": "Goal name",
                        "type": "short/long",
                        "amount": 50000,
                        "year": 2025,
                        "priority": "high/medium/low",
                        "reasoning": "Why this goal is appropriate for this user",
                        "steps": ["Step 1", "Step 2"],
                        "challenges": ["Challenge 1", "Challenge 2"],
                        "monthly_savings_needed": 5000
                    }}
                ]
            }}
            
            Consider:
            - User's specific request (e.g., "buy gold", "house down payment", "retirement")
            - Current financial position
            - Realistic timelines and amounts
            - Indian financial context (tax benefits, investment options)
            - Priority based on financial health
            
            Make goals specific to the user's request, not generic.
            """
            
            logging.info(f"📝 AI GOAL SUGGESTIONS: Prompt created - Length: {len(goal_prompt)} characters")
            logging.info(f"📝 AI GOAL SUGGESTIONS: Prompt preview: {goal_prompt[:200]}...")
            
            # Call Gemini API for goal suggestions
            logging.info("🤖 AI GOAL SUGGESTIONS: Calling Gemini API...")
            response = self._call_gemini_api(goal_prompt)
            
            if response and response.get('candidates'):
                content = response['candidates'][0]['content']['parts'][0]['text']
                logging.info(f"✅ AI GOAL SUGGESTIONS: Gemini API response received - Length: {len(content)} characters")
                logging.info(f"📄 AI GOAL SUGGESTIONS: Response preview: {content[:200]}...")
                
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    suggestions_data = json.loads(json_match.group())
                    suggestions = suggestions_data.get('suggestions', [])
                    logging.info(f"✅ AI GOAL SUGGESTIONS: JSON parsed successfully - {len(suggestions)} suggestions extracted")
                    for i, suggestion in enumerate(suggestions, 1):
                        logging.info(f"🎯 AI GOAL SUGGESTIONS: Suggestion {i}: {suggestion.get('name', 'Unknown')} - ₹{suggestion.get('amount', 0):,.0f}")
                    return suggestions
                else:
                    logging.warning("⚠️ AI GOAL SUGGESTIONS: No JSON found in Gemini response")
                    logging.info(f"📄 AI GOAL SUGGESTIONS: Full response: {content}")
            else:
                logging.error("❌ AI GOAL SUGGESTIONS: No response from Gemini API")
                    
        except Exception as e:
            logging.error(f"❌ AI GOAL SUGGESTIONS: Error generating AI goal suggestions: {e}")
        
        # Fallback suggestions if AI fails
        logging.info("🔄 AI GOAL SUGGESTIONS: Using fallback suggestions")
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
        
        logging.info(f"🔄 AI GOAL SUGGESTIONS: Fallback suggestions created: {len(fallback_suggestions)}")
        return fallback_suggestions
    
    def _scenario_modeling_analysis(self, user_message: str, financial_context: Dict) -> Dict:
        """Custom scenario modeling analysis"""
        analysis = {
            'text': "Scenario Modeling Analysis:\n\n",
            'recommendations': [],
            'insights': []
        }
        
        # Extract scenario details from user message
        user_message_lower = user_message.lower()
        
        if any(word in user_message_lower for word in ['loan', 'debt', 'pay off']):
            analysis['text'] += "• Loan Repayment Scenario:\n"
            analysis['text'] += "  - Calculate interest savings\n"
            analysis['text'] += "  - Consider opportunity cost\n"
            analysis['text'] += "  - Maintain emergency fund\n"
            analysis['text'] += "  - Evaluate impact on goals\n\n"
            
            analysis['recommendations'].extend([
                "Calculate interest savings vs investment returns",
                "Maintain emergency fund before debt repayment",
                "Consider debt consolidation if multiple loans"
            ])
            
        elif any(word in user_message_lower for word in ['invest', 'investment']):
            analysis['text'] += "• Investment Scenario:\n"
            analysis['text'] += "  - Assess risk tolerance\n"
            analysis['text'] += "  - Consider time horizon\n"
            analysis['text'] += "  - Diversify across asset classes\n"
            analysis['text'] += "  - Account for taxes and inflation\n\n"
            
            analysis['recommendations'].extend([
                "Start with SIPs for systematic investing",
                "Diversify across equity and debt",
                "Consider tax-efficient instruments"
            ])
            
        else:
            analysis['text'] += "• General Scenario Analysis:\n"
            analysis['text'] += "  - Evaluate impact on financial goals\n"
            analysis['text'] += "  - Consider risk and return trade-offs\n"
            analysis['text'] += "  - Account for taxes and inflation\n"
            analysis['text'] += "  - Maintain emergency fund\n\n"
            
            analysis['recommendations'].extend([
                "Evaluate impact on overall financial health",
                "Consider opportunity costs",
                "Maintain adequate emergency fund"
            ])
        
        analysis['text'] += "• Always model multiple scenarios for comprehensive analysis."
        analysis['insights'].extend([
            "Scenario-based financial planning",
            "Risk-return optimization"
        ])
        
        return analysis
    
    def _cash_flow_analysis(self, user_message: str, financial_context: Dict) -> Dict:
        """Custom cash flow analysis"""
        analysis = {
            'text': "Cash Flow Analysis:\n\n",
            'recommendations': [],
            'insights': []
        }
        
        # Emergency fund analysis
        metrics = financial_context.get('metrics', {})
        emergency_ratio = metrics.get('emergency_fund_ratio', 0)
        
        analysis['text'] += "• Emergency Fund Status:\n"
        if emergency_ratio >= 100:
            analysis['text'] += "  - Excellent emergency fund coverage\n"
            analysis['insights'].append("Strong emergency fund")
        elif emergency_ratio >= 50:
            analysis['text'] += "  - Good emergency fund coverage\n"
            analysis['recommendations'].append("Consider increasing emergency fund")
        else:
            analysis['text'] += "  - Emergency fund needs attention\n"
            analysis['recommendations'].append("Build emergency fund immediately")
        
        # Cash management recommendations
        analysis['text'] += "\n• Cash Management:\n"
        analysis['text'] += "  - Maintain 3-6 months of expenses\n"
        analysis['text'] += "  - Use high-yield savings accounts\n"
        analysis['text'] += "  - Consider liquid mutual funds\n"
        analysis['text'] += "  - Separate emergency and investment funds\n\n"
        
        analysis['text'] += "• Regular cash flow monitoring recommended."
        
        analysis['recommendations'].extend([
            "Build adequate emergency fund",
            "Use high-yield savings accounts",
            "Monitor cash flow regularly"
        ])
        
        analysis['insights'].extend([
            "Cash flow optimization",
            "Liquidity management"
        ])
        
        return analysis
    
    def _general_financial_analysis(self, user_message: str, financial_context: Dict) -> Dict:
        """General financial analysis for unspecified queries"""
        analysis = {
            'text': "General Financial Analysis:\n\n",
            'recommendations': [],
            'insights': []
        }
        
        analysis['text'] += "• Comprehensive Financial Health:\n"
        analysis['text'] += "  - Review your financial goals regularly\n"
        analysis['text'] += "  - Maintain adequate emergency savings\n"
        analysis['text'] += "  - Diversify your investments\n"
        analysis['text'] += "  - Optimize tax-saving opportunities\n"
        analysis['text'] += "  - Manage debt efficiently\n\n"
        
        analysis['text'] += "• Consider consulting a financial advisor for personalized guidance."
        
        analysis['recommendations'].extend([
            "Set clear financial goals",
            "Build emergency fund",
            "Diversify investments",
            "Optimize tax savings"
        ])
        
        analysis['insights'].extend([
            "Comprehensive financial planning",
            "Holistic approach to wealth management"
        ])
        
        return analysis
    
    def _lending_borrowing_analysis(self, user_message: str, financial_context: Dict) -> Dict:
        """Analyze lending and borrowing scenarios with comprehensive financial context"""
        try:
            portfolio = financial_context.get('portfolio', {})
            metrics = financial_context.get('metrics', {})
            net_worth = portfolio.get('net_worth', 0)
            emergency_fund = metrics.get('emergency_fund_ratio', 0)
            
            # Extract additional context from user_profile
            user_profile = financial_context.get('profile', {})
            user_goals = user_profile.get('goals', [])
            cash_assets = user_profile.get('cash_assets', [])
            upcoming_transactions = user_profile.get('upcoming_transactions', {})
            trust_rating = user_profile.get('trust_rating', {})
            
            # Calculate total cash
            total_cash = sum(a.get('amount', 0) for a in cash_assets)
            
            # Extract lending amount from user message
            import re
            amount_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', user_message)
            lending_amount = 0
            if amount_match:
                lending_amount = float(amount_match.group(1).replace(',', ''))
            
            # Calculate comprehensive affordability metrics
            upcoming_total = upcoming_transactions.get('total_amount', 0)
            cash_after_lending = total_cash - lending_amount
            cash_after_expenses = cash_after_lending - upcoming_total
            
            # Calculate goals impact
            total_goals_amount = sum(float(goal.get('amount', 0)) for goal in user_goals)
            goals_impact_ratio = (lending_amount / total_goals_amount * 100) if total_goals_amount > 0 else 0
            
            # Calculate affordability score
            affordability_score = 0
            if cash_after_expenses > 0:
                cash_score = min(100, (cash_after_expenses / lending_amount) * 50) if lending_amount > 0 else 100
                net_worth_ratio = lending_amount / net_worth if net_worth > 0 else 1
                net_worth_score = max(0, 50 - (net_worth_ratio * 25))
                affordability_score = min(100, cash_score + net_worth_score)
            
            # Risk assessment
            risk_level = 'low'
            if cash_after_expenses < 0:
                risk_level = 'high'
            elif cash_after_expenses < (upcoming_total * 2):
                risk_level = 'medium'
            
            # Trust level analysis
            trust_level = trust_rating.get('overall_trust_level', 'unknown')
            trust_score = trust_rating.get('average_rating', 0)
            
            # Create comprehensive analysis
            analysis = f"""
            **Comprehensive Lending Analysis for ₹{lending_amount:,.0f}**
            
            **Your Financial Position:**
            • Net Worth: ₹{net_worth:,.0f}
            • Total Cash Assets: ₹{total_cash:,.0f}
            • Emergency Fund Coverage: {emergency_fund:.1f}% of recommended
            • Upcoming Expenses (20 days): ₹{upcoming_total:,.0f}
            
            **Affordability Analysis:**
            • Cash after lending: ₹{cash_after_lending:,.0f}
            • Cash after expenses: ₹{cash_after_expenses:,.0f}
            • Affordability Score: {affordability_score:.1f}/100
            • Risk Level: {risk_level.upper()}
            
            **Goals Impact:**
            • Total Goals Value: ₹{total_goals_amount:,.0f}
            • Lending Impact: {goals_impact_ratio:.1f}% of goals
            • Will delay goals: {'Yes' if goals_impact_ratio > 20 else 'No'}
            
            **Trust Analysis:**
            • Borrower Trust Level: {trust_level.upper()}
            • Trust Score: {trust_score:.1f}/10
            • Total Transactions: {trust_rating.get('total_transactions', 0)}
            """
            
            # Generate recommendation
            if affordability_score >= 80 and trust_level in ['excellent', 'good']:
                recommendation = 'APPROVE'
                reason = 'Strong financial position and good trust rating'
                analysis += f"""
                
                ✅ **RECOMMENDATION: APPROVE**
                
                **Why it's safe:**
                • High affordability score ({affordability_score:.1f}/100)
                • Good trust rating ({trust_level})
                • Sufficient cash buffer after expenses
                • Won't significantly impact your goals
                
                **Best Practices:**
                • Document the agreement clearly
                • Set realistic repayment timeline
                • Monitor repayment progress
                • Rate the borrower after repayment
                """
            elif affordability_score >= 60 and trust_level == 'excellent':
                recommendation = 'APPROVE_WITH_CAUTION'
                reason = 'Moderate financial position but excellent trust rating'
                analysis += f"""
                
                ⚠️ **RECOMMENDATION: APPROVE WITH CAUTION**
                
                **Considerations:**
                • Moderate affordability score ({affordability_score:.1f}/100)
                • Excellent trust rating provides confidence
                • Monitor your cash flow closely
                
                **Suggestions:**
                • Consider reducing the amount slightly
                • Set shorter repayment timeline
                • Keep emergency fund intact
                """
            elif affordability_score >= 70 and trust_level == 'good':
                recommendation = 'APPROVE_WITH_CAUTION'
                reason = 'Good financial position but moderate trust rating'
                analysis += f"""
                
                ⚠️ **RECOMMENDATION: APPROVE WITH CAUTION**
                
                **Considerations:**
                • Good affordability score ({affordability_score:.1f}/100)
                • Moderate trust rating requires careful monitoring
                
                **Suggestions:**
                • Set clear repayment terms
                • Regular follow-up on repayment
                • Consider smaller amount if uncertain
                """
            elif affordability_score < 50:
                recommendation = 'REJECT'
                reason = 'Insufficient financial capacity'
                analysis += f"""
                
                ❌ **RECOMMENDATION: REJECT**
                
                **Why it's not advisable:**
                • Low affordability score ({affordability_score:.1f}/100)
                • Would leave insufficient cash buffer
                • Could impact emergency fund adequacy
                • May delay your financial goals
                
                **Alternatives:**
                • Consider a smaller amount
                • Strengthen your emergency fund first
                • Explore non-monetary ways to help
                """
            else:
                recommendation = 'REJECT'
                reason = 'Poor trust rating or financial constraints'
                analysis += f"""
                
                ❌ **RECOMMENDATION: REJECT**
                
                **Concerns:**
                • Poor trust rating ({trust_level})
                • Financial constraints present
                • High risk to your financial stability
                
                **Recommendations:**
                • Wait for better financial position
                • Build trust rating first
                • Consider alternative assistance methods
                """
            
            # Add financial planning impact
            analysis += f"""
            
            **Impact on Financial Planning:**
            • Emergency Fund: {'⚠️ At risk' if cash_after_expenses < (upcoming_total * 2) else '✅ Safe'}
            • Investment Goals: {'⚠️ May be delayed' if goals_impact_ratio > 20 else '✅ Minimal impact'}
            • Cash Flow: {'⚠️ Tight' if cash_after_expenses < upcoming_total else '✅ Comfortable'}
            • Risk Level: {risk_level.upper()}
            
            **Monitoring Recommendations:**
            • Track repayment timeline closely
            • Monitor your cash flow
            • Update trust rating after repayment
            • Adjust future lending based on experience
            """
            
            # Generate recommendations
            recommendations = []
            
            if recommendation == 'APPROVE':
                recommendations.append({
                    'title': 'Proceed with Lending',
                    'priority': 'Medium',
                    'description': f'Your financial position supports lending ₹{lending_amount:,.0f}',
                    'action': 'Document agreement clearly',
                    'save': 'Maintain relationship while protecting finances',
                    'icon': 'opportunity'
                })
            elif recommendation == 'APPROVE_WITH_CAUTION':
                recommendations.append({
                    'title': 'Proceed with Caution',
                    'priority': 'High',
                    'description': f'Lend ₹{lending_amount:,.0f} but monitor closely',
                    'action': 'Set clear terms and timeline',
                    'save': 'Balance helping with financial safety',
                    'icon': 'warning'
                })
            else:
                recommendations.append({
                    'title': 'Reconsider Lending',
                    'priority': 'High',
                    'description': f'Financial constraints make lending ₹{lending_amount:,.0f} risky',
                    'action': 'Consider smaller amount or alternatives',
                    'save': 'Protect your financial stability',
                    'icon': 'alert'
                })
            
            return {
                'text': analysis,
                'recommendations': recommendations,
                'metrics': {
                    'affordability_score': affordability_score,
                    'risk_level': risk_level,
                    'cash_after_expenses': cash_after_expenses,
                    'goals_impact_ratio': goals_impact_ratio,
                    'trust_level': trust_level
                }
            }
            
        except Exception as e:
            logging.error(f"Error in lending analysis: {e}")
            return {
                'text': f"Error analyzing lending request: {str(e)}",
                'recommendations': [],
                'metrics': {}
            }
    
    def _enhance_response_with_insights(self, analysis_result: Dict, financial_context: Dict) -> Dict:
        """Enhance response with additional insights"""
        enhanced = analysis_result.copy()
        
        # Add contextual insights with user's actual data
        metrics = financial_context.get('metrics', {})
        portfolio = financial_context.get('portfolio', {})
        
        if metrics.get('net_worth', 0) > 0:
            enhanced['insights'].append(f"Net Worth: ₹{metrics['net_worth']:,.0f}")
        
        if metrics.get('emergency_fund_ratio', 0) > 0:
            enhanced['insights'].append(f"Emergency Fund Coverage: {metrics['emergency_fund_ratio']:.1f}%")
        
        # Add asset allocation insights
        assets = portfolio.get('assets', [])
        if assets:
            total_assets = sum(asset['value'] for asset in assets)
            equity_assets = sum(asset['value'] for asset in assets 
                              if 'equity' in asset.get('type', '').lower() or 
                                 'stock' in asset.get('type', '').lower())
            if total_assets > 0:
                equity_ratio = (equity_assets / total_assets) * 100
                enhanced['insights'].append(f"Equity Allocation: {equity_ratio:.1f}%")
        
        # Add debt insights
        liabilities = portfolio.get('liabilities', [])
        if liabilities:
            total_debt = sum(liability['value'] for liability in liabilities)
            if total_debt > 0:
                debt_ratio = (total_debt / metrics.get('net_worth', 1)) * 100
                enhanced['insights'].append(f"Debt Ratio: {debt_ratio:.1f}%")
        
        # Add Indian context insights
        enhanced['insights'].extend([
            "Indian financial market optimized",
            "Tax-efficient strategies applied"
        ])
        
        return enhanced
    
    def _generate_fallback_response(self, user_message: str, financial_data: Dict) -> Dict:
        """Generate intelligent fallback response"""
        user_message_lower = user_message.lower()
        
        if any(word in user_message_lower for word in ['loan', 'debt', 'pay off']):
            return {
                'response': "For debt management, prioritize high-interest debts first while maintaining your emergency fund. Consider debt consolidation for better rates and calculate the opportunity cost of using savings for debt repayment.",
                'analysis_type': 'debt_management',
                'confidence': 0.7,
                'recommendations': ["Prioritize high-interest debts", "Maintain emergency fund", "Consider debt consolidation"],
                'insights': ["Debt management strategy", "Emergency fund protection"],
                'requires_financial_data': True,
                'agent_type': 'custom_financial_agent'
            }
        else:
            return {
                'response': "I can help with comprehensive financial planning, investment strategies, tax optimization, and debt management. Please ask me specific questions about your financial goals.",
                'analysis_type': 'general',
                'confidence': 0.5,
                'recommendations': ["Define financial goals", "Create savings plan", "Consult financial advisor"],
                'insights': ["General financial guidance", "Professional advice recommended"],
                'requires_financial_data': True,
                'agent_type': 'custom_financial_agent'
            }
    
    def _extract_portfolio_data(self, financial_data: Dict) -> Dict:
        """Extract portfolio data with enhanced analysis"""
        portfolio = {
            'net_worth': 0,
            'assets': [],
            'liabilities': [],
            'asset_allocation': {},
            'cash_position': 0
        }
        
        if 'fetch_net_worth' in financial_data and financial_data['fetch_net_worth']:
            net_worth_data = financial_data['fetch_net_worth'].get('netWorthResponse', {})
            
            if 'totalNetWorthValue' in net_worth_data:
                portfolio['net_worth'] = float(net_worth_data['totalNetWorthValue']['units'])
            
            if 'assetValues' in net_worth_data:
                for asset in net_worth_data['assetValues']:
                    asset_type = asset.get('netWorthAttribute', 'UNKNOWN')
                    value = float(asset.get('value', {}).get('units', 0))
                    portfolio['assets'].append({
                        'type': asset_type,
                        'value': value
                    })
                    
                    if asset_type not in portfolio['asset_allocation']:
                        portfolio['asset_allocation'][asset_type] = 0
                    portfolio['asset_allocation'][asset_type] += value
            
            if 'liabilityValues' in net_worth_data:
                for liability in net_worth_data['liabilityValues']:
                    liability_type = liability.get('netWorthAttribute', 'UNKNOWN')
                    value = float(liability.get('value', {}).get('units', 0))
                    portfolio['liabilities'].append({
                        'type': liability_type,
                        'value': value
                    })
        
        return portfolio
    
    def _extract_transaction_data(self, financial_data: Dict) -> Dict:
        """Extract and process transaction data"""
        transactions = {
            'bank_transactions': [],
            'mf_transactions': [],
            'stock_transactions': [],
            'recent_activity': [],
            'recurring_transactions': [],
            'upcoming_transactions': [],
            'emi_transactions': [],
            'monthly_expenses': 0,
            'total_transactions': 0
        }
        
        # Extract bank transactions
        if 'fetch_bank_transactions' in financial_data and financial_data['fetch_bank_transactions']:
            bank_data = financial_data['fetch_bank_transactions']
            if 'bankTransactionsResponse' in bank_data:
                for account in bank_data['bankTransactionsResponse'].get('accounts', []):
                    for transaction in account.get('transactions', []):
                        amount = float(transaction.get('amount', {}).get('units', 0))
                        description = transaction.get('description', '').lower()
                        date = transaction.get('date', '')
                        
                        transaction_data = {
                            'amount': amount,
                            'description': transaction.get('description', ''),
                            'date': date
                        }
                        
                        transactions['bank_transactions'].append(transaction_data)
                        transactions['total_transactions'] += 1
                        
                        # Identify EMIs and loan payments
                        if any(keyword in description for keyword in ['emi', 'loan', 'mortgage', 'credit card payment']):
                            transactions['emi_transactions'].append(transaction_data)
                            transactions['recurring_transactions'].append(transaction_data)
                        
                        # Identify recurring payments and subscriptions
                        elif any(keyword in description for keyword in ['subscription', 'auto-debit', 'recurring', 'monthly', 'netflix', 'gym', 'membership']):
                            transactions['recurring_transactions'].append(transaction_data)
                        
                        # Identify upcoming large expenses (negative amounts)
                        elif amount < -10000:
                            transactions['upcoming_transactions'].append(transaction_data)
                        
                        # Calculate monthly expenses (negative amounts)
                        if amount < 0:
                            transactions['monthly_expenses'] += abs(amount)
        
        # Extract mutual fund transactions
        if 'fetch_mf_transactions' in financial_data and financial_data['fetch_mf_transactions']:
            mf_data = financial_data['fetch_mf_transactions']
            if 'mfTransactionsResponse' in mf_data:
                for transaction in mf_data['mfTransactionsResponse'].get('transactions', []):
                    transactions['mf_transactions'].append({
                        'amount': float(transaction.get('amount', {}).get('units', 0)),
                        'description': transaction.get('description', ''),
                        'date': transaction.get('date', '')
                    })
                    transactions['total_transactions'] += 1
        
        # Extract stock transactions
        if 'fetch_stock_transactions' in financial_data and financial_data['fetch_stock_transactions']:
            stock_data = financial_data['fetch_stock_transactions']
            if 'stockTransactionsResponse' in stock_data:
                for transaction in stock_data['stockTransactionsResponse'].get('transactions', []):
                    transactions['stock_transactions'].append({
                        'amount': float(transaction.get('amount', {}).get('units', 0)),
                        'description': transaction.get('description', ''),
                        'date': transaction.get('date', '')
                    })
                    transactions['total_transactions'] += 1
        
        return transactions
    
    def _extract_credit_data(self, financial_data: Dict) -> Dict:
        """Extract credit data"""
        credit = {
            'score': 0,
            'accounts': [],
            'payment_history': []
        }
        
        if 'fetch_credit_report' in financial_data and financial_data['fetch_credit_report']:
            credit_data = financial_data['fetch_credit_report']
            if 'creditReportResponse' in credit_data:
                report = credit_data['creditReportResponse']
                
                if 'creditScore' in report:
                    credit['score'] = int(report['creditScore'].get('score', 0))
                
                if 'accounts' in report:
                    for account in report['accounts']:
                        credit['accounts'].append({
                            'type': account.get('accountType', 'UNKNOWN'),
                            'balance': float(account.get('balance', {}).get('units', 0)),
                            'limit': float(account.get('creditLimit', {}).get('units', 0))
                        })
        
        return credit
    
    def _call_gemini_api(self, prompt: str) -> Optional[Dict]:
        """Call Gemini API with custom error handling"""
        max_retries = 2
        timeout = 10
        
        logging.info("🤖 Custom Agent: Calling Gemini API")
        logging.info(f"📝 Custom Agent: Prompt length: {len(prompt)} characters")
        
        for attempt in range(max_retries):
            try:
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                
                logging.info(f"🔄 Custom Agent: Gemini API attempt {attempt + 1}/{max_retries}")
                
                response = requests.post(
                    self.gemini_api_url, 
                    json=payload, 
                    timeout=timeout,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    logging.info("✅ Custom Agent: Gemini API call successful")
                    return response.json()
                else:
                    logging.error(f"❌ Custom Agent: Gemini API error: {response.status_code} {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                logging.error(f"⏰ Custom Agent: Gemini API timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return None
            except Exception as e:
                logging.error(f"💥 Custom Agent: Error calling Gemini API: {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
                return None
        
        logging.error("❌ Custom Agent: All Gemini API attempts failed")
        return None
    
    def generate_recommendations(self, financial_data: Dict, user_goals: List[Dict] = None) -> List[Dict]:
        """Generate personalized financial recommendations"""
        logging.info("🎯 Custom Agent: Generating recommendations")
        
        try:
            # Prepare financial context
            financial_context = self._prepare_comprehensive_context(financial_data, {'goals': user_goals})
            
            # Generate recommendations based on financial profile
            recommendations = []
            
            # Portfolio recommendations
            portfolio = financial_context.get('portfolio', {})
            metrics = financial_context.get('metrics', {})
            
            # Emergency fund recommendation
            emergency_ratio = metrics.get('emergency_fund_ratio', 0)
            if emergency_ratio < 50:
                recommendations.append({
                    'title': 'Build Emergency Fund',
                    'priority': 'High',
                    'description': 'Your emergency fund needs attention. Aim for 3-6 months of expenses.',
                    'action': 'Start SIP in liquid funds',
                    'save': 'Financial security during emergencies',
                    'icon': 'alert'
                })
            
            # Debt management recommendation
            debt_ratio = metrics.get('debt_to_income_ratio', 0)
            if debt_ratio > 40:
                recommendations.append({
                    'title': 'Prioritize Debt Repayment',
                    'priority': 'High',
                    'description': 'Focus on high-interest debts first while maintaining emergency fund.',
                    'action': 'Create debt repayment plan',
                    'save': 'Reduce interest payments',
                    'icon': 'spending'
                })
            
            # Tax optimization recommendation
            recommendations.append({
                'title': 'Optimize Tax Savings',
                'priority': 'Medium',
                'description': 'Maximize Section 80C deductions through ELSS, EPF, and tax-saving FDs.',
                'action': 'Review tax-saving investments',
                'save': 'Up to ₹1.5L in tax savings',
                'icon': 'tax'
            })
            
            # Investment diversification recommendation
            investment_ratio = metrics.get('investment_ratio', 0)
            if investment_ratio < 30:
                recommendations.append({
                    'title': 'Increase Investment Allocation',
                    'priority': 'Medium',
                    'description': 'Consider increasing equity exposure for long-term growth.',
                    'action': 'Start SIPs in equity funds',
                    'save': 'Higher long-term returns',
                    'icon': 'portfolio'
                })
            
            # Goal-based recommendation
            if user_goals:
                recommendations.append({
                    'title': 'Review Financial Goals',
                    'priority': 'Medium',
                    'description': 'Regularly review and adjust your financial goals.',
                    'action': 'Update goal progress',
                    'save': 'Better goal achievement',
                    'icon': 'opportunity'
                })
            
            # Default recommendation if none generated
            if not recommendations:
                recommendations.append({
                    'title': 'Start Financial Planning',
                    'priority': 'Medium',
                    'description': 'Begin systematic financial planning for better wealth creation.',
                    'action': 'Create financial plan',
                    'save': 'Improved financial health',
                    'icon': 'portfolio'
                })
            
            logging.info(f"✅ Custom Agent: Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logging.error(f"❌ Custom Agent: Error generating recommendations: {e}")
            return [{
                'title': 'Financial Planning',
                'priority': 'Medium',
                'description': 'Consider comprehensive financial planning for better wealth management.',
                'action': 'Consult financial advisor',
                'save': 'Improved financial outcomes',
                'icon': 'portfolio'
            }]
    
    def generate_insights(self, financial_data: Dict, user_goals: List[Dict] = None) -> List[Dict]:
        """Generate personalized financial insights"""
        logging.info("🎯 Custom Agent: Generating insights")
        logging.info(f"📊 Custom Agent: Financial data keys: {list(financial_data.keys()) if financial_data else 'None'}")
        logging.info(f"🎯 Custom Agent: User goals: {user_goals}")
        
        try:
            # Prepare financial context
            financial_context = self._prepare_comprehensive_context(financial_data, {'goals': user_goals})
            logging.info(f"📈 Custom Agent: Financial context prepared - Net worth: ₹{financial_context.get('portfolio', {}).get('net_worth', 0):,.0f}")
            
            # Generate insights based on financial profile
            insights = []
            
            # Portfolio insights
            portfolio = financial_context.get('portfolio', {})
            metrics = financial_context.get('metrics', {})
            transactions = financial_context.get('transactions', {})
            
            # Upcoming expenses analysis
            upcoming_expenses = self._analyze_upcoming_expenses(transactions, financial_context)
            if upcoming_expenses:
                insights.extend(upcoming_expenses)
            
            # EMI and auto-debit analysis
            emi_insights = self._analyze_emi_and_autodebits(transactions, financial_context)
            if emi_insights:
                insights.extend(emi_insights)
            
            # Cash flow analysis
            cash_flow_insights = self._analyze_cash_flow(transactions, financial_context)
            if cash_flow_insights:
                insights.extend(cash_flow_insights)
            
            # Salary pattern analysis
            salary_insights = self._analyze_salary_patterns(transactions, financial_context)
            if salary_insights:
                insights.extend(salary_insights)
            
            # Tax optimization insight (always relevant)
            insights.append({
                'title': 'Tax Optimization Required',
                'priority': 'High Priority',
                'description': 'Invest ₹1,50,000 in ELSS by June 15th to save ₹45,000 in taxes this year. Our AI analysis shows you have sufficient funds in your savings account.',
                'action': 'Take Action',
                'save': 'Save ₹45,000',
                'icon': 'tax'
            })
            
            # Portfolio drift detection
            equity_allocation = portfolio.get('equity_allocation', 0)
            if equity_allocation > 70:
                insights.append({
                    'title': 'Portfolio Drift Detected',
                    'priority': 'Medium Priority',
                    'description': f'Your portfolio has drifted from your target allocation. Consider rebalancing to optimize risk/return based on AI analysis. Equity exposure is {equity_allocation - 60}% higher than your risk profile suggests.',
                    'action': 'View Details',
                    'save': '+2.3% potential',
                    'icon': 'portfolio'
                })
            
            # Spending pattern analysis
            if transactions.get('total_transactions', 0) > 10:
                insights.append({
                    'title': 'Spending Pattern Analysis',
                    'priority': 'Informational',
                    'description': 'Your discretionary spending increased by 15% this month. The main categories with increases were dining out (+32%) and entertainment (+24%).',
                    'action': 'See Budget Plan',
                    'save': '',
                    'icon': 'spending'
                })
            
            # Capital gain opportunity
            if portfolio.get('capital_gains', 0) > 50000:
                insights.append({
                    'title': 'Capital Gain Opportunity',
                    'priority': 'Opportunity',
                    'description': f'Offset your recent capital gains of ₹{portfolio.get("capital_gains", 0):,.0f} by selling your underperforming mutual fund units, potentially saving ₹{portfolio.get("capital_gains", 0) * 0.25:,.0f} in taxes.',
                    'action': 'Explore Strategy',
                    'save': f'Save ₹{portfolio.get("capital_gains", 0) * 0.25:,.0f}',
                    'icon': 'opportunity'
                })
            
            # Emergency fund insight
            emergency_ratio = metrics.get('emergency_fund_ratio', 0)
            if emergency_ratio >= 100:
                insights.append({
                    'title': 'Strong Emergency Fund',
                    'priority': 'Opportunity',
                    'description': 'Your emergency fund is well-maintained. Consider investing excess funds for better returns.',
                    'action': 'Consider investment opportunities',
                    'save': 'Financial security',
                    'icon': 'opportunity'
                })
            elif emergency_ratio < 50:
                insights.append({
                    'title': 'Emergency Fund Alert',
                    'priority': 'High Priority',
                    'description': 'Your emergency fund needs immediate attention. Aim to build 6 months of expenses.',
                    'action': 'Build emergency fund',
                    'save': 'Financial security',
                    'icon': 'alert'
                })
            
            # Debt insight
            debt_ratio = metrics.get('debt_to_income_ratio', 0)
            if debt_ratio > 40:
                insights.append({
                    'title': 'High Debt Level',
                    'priority': 'High Priority',
                    'description': f'Your debt-to-income ratio is {debt_ratio:.1f}%, which is above the recommended 40%. Focus on debt reduction to improve financial health.',
                    'action': 'Create debt repayment plan',
                    'save': 'Reduce interest payments',
                    'icon': 'spending'
                })
            elif debt_ratio > 20:
                insights.append({
                    'title': 'Moderate Debt Level',
                    'priority': 'Medium Priority',
                    'description': f'Your debt-to-income ratio is {debt_ratio:.1f}%, which is manageable but could be optimized for better financial health.',
                    'action': 'Review debt structure',
                    'save': 'Better debt management',
                    'icon': 'portfolio'
                })
            
            # Investment insight
            investment_ratio = metrics.get('investment_ratio', 0)
            if investment_ratio < 20:
                insights.append({
                    'title': 'Low Investment Allocation',
                    'priority': 'Medium Priority',
                    'description': f'Your investment allocation is {investment_ratio:.1f}% of net worth. Consider increasing allocation for better long-term returns.',
                    'action': 'Start systematic investing',
                    'save': 'Higher long-term returns',
                    'icon': 'portfolio'
                })
            elif investment_ratio > 60:
                insights.append({
                    'title': 'High Investment Allocation',
                    'priority': 'Informational',
                    'description': f'Your investment allocation is {investment_ratio:.1f}% of net worth, which is well-balanced for growth.',
                    'action': 'Review portfolio performance',
                    'save': 'Maintain growth',
                    'icon': 'opportunity'
                })
            
            # Insurance coverage insight
            insurance_data = financial_data.get('fetch_insurance', {})
            if insurance_data and insurance_data.get('totalCoverage', 0) < 1000000:
                insights.append({
                    'title': 'Insurance Coverage Review',
                    'priority': 'Medium Priority',
                    'description': 'Your insurance coverage may be insufficient. Consider increasing life insurance coverage to protect your family.',
                    'action': 'Review insurance needs',
                    'save': 'Family protection',
                    'icon': 'alert'
                })
            
            # Net worth insight
            net_worth = metrics.get('net_worth', 0)
            if net_worth > 0:
                insights.append({
                    'title': 'Net Worth Analysis',
                    'priority': 'Informational',
                    'description': f'Your current net worth is ₹{net_worth:,.0f}. Continue building wealth through smart investments and savings.',
                    'action': 'Track net worth growth',
                    'save': 'Better financial awareness',
                    'icon': 'portfolio'
                })
            
            # Default insight if none generated
            if not insights:
                insights.append({
                    'title': 'Financial Health Overview',
                    'priority': 'Informational',
                    'description': 'Regular financial review helps maintain good financial health. Schedule periodic reviews to stay on track.',
                    'action': 'Schedule financial review',
                    'save': 'Better financial outcomes',
                    'icon': 'portfolio'
                })
            
            logging.info(f"✅ Custom Agent: Generated {len(insights)} insights")
            return insights
            
        except Exception as e:
            logging.error(f"❌ Custom Agent: Error generating insights: {e}")
            logging.error(f"❌ Custom Agent: Exception details: {str(e)}")
            return [{
                'title': 'Financial Review',
                'priority': 'Informational',
                'description': 'Regular financial reviews help maintain good financial health.',
                'action': 'Schedule financial review',
                'save': 'Better financial outcomes',
                'icon': 'portfolio'
            }]
    
    def _analyze_upcoming_expenses(self, transactions: Dict, financial_context: Dict) -> List[Dict]:
        """Analyze upcoming expenses and recurring payments"""
        insights = []
        
        # Extract recurring transactions
        recurring_transactions = transactions.get('recurring_transactions', [])
        upcoming_transactions = transactions.get('upcoming_transactions', [])
        
        # Analyze EMIs and loan payments
        emi_transactions = [t for t in recurring_transactions if any(keyword in t.get('description', '').lower() 
                                                                    for keyword in ['emi', 'loan', 'mortgage', 'credit card'])]
        
        if emi_transactions:
            total_emi = sum(t.get('amount', 0) for t in emi_transactions)
            insights.append({
                'title': 'EMI Payment Alert',
                'priority': 'High Priority',
                'description': f'You have ₹{total_emi:,.0f} in EMI payments due this month. Ensure sufficient funds are available to avoid late fees.',
                'action': 'Review EMI schedule',
                'save': 'Avoid late fees',
                'icon': 'alert'
            })
        
        # Analyze upcoming large expenses
        large_expenses = [t for t in upcoming_transactions if t.get('amount', 0) > 10000]
        if large_expenses:
            total_large_expenses = sum(t.get('amount', 0) for t in large_expenses)
            insights.append({
                'title': 'Large Expense Alert',
                'priority': 'Medium Priority',
                'description': f'You have ₹{total_large_expenses:,.0f} in upcoming large expenses. Plan your cash flow accordingly.',
                'action': 'Review cash flow',
                'save': 'Better planning',
                'icon': 'spending'
            })
        
        # Analyze subscription and auto-debit payments
        auto_debits = [t for t in recurring_transactions if any(keyword in t.get('description', '').lower() 
                                                               for keyword in ['subscription', 'auto-debit', 'recurring', 'monthly'])]
        
        if auto_debits:
            total_auto_debits = sum(t.get('amount', 0) for t in auto_debits)
            insights.append({
                'title': 'Auto-Debit Review',
                'priority': 'Medium Priority',
                'description': f'You have ₹{total_auto_debits:,.0f} in auto-debit payments monthly. Review subscriptions to optimize expenses.',
                'action': 'Review subscriptions',
                'save': 'Optimize expenses',
                'icon': 'spending'
            })
        
        return insights
    
    def _analyze_emi_and_autodebits(self, transactions: Dict, financial_context: Dict) -> List[Dict]:
        """Analyze EMI and auto-debit patterns"""
        insights = []
        
        # Get monthly income for ratio analysis
        monthly_income = financial_context.get('monthly_income', 50000)
        
        # Analyze EMI burden
        emi_transactions = transactions.get('emi_transactions', [])
        if emi_transactions:
            total_emi = sum(t.get('amount', 0) for t in emi_transactions)
            emi_ratio = (total_emi / monthly_income) * 100 if monthly_income > 0 else 0
            
            if emi_ratio > 50:
                insights.append({
                    'title': 'High EMI Burden',
                    'priority': 'High Priority',
                    'description': f'Your EMI payments ({emi_ratio:.1f}% of income) are high. Consider debt consolidation or restructuring.',
                    'action': 'Review debt strategy',
                    'save': 'Reduce financial stress',
                    'icon': 'alert'
                })
            elif emi_ratio > 30:
                insights.append({
                    'title': 'Moderate EMI Burden',
                    'priority': 'Medium Priority',
                    'description': f'Your EMI payments ({emi_ratio:.1f}% of income) are manageable but monitor closely.',
                    'action': 'Monitor EMI payments',
                    'save': 'Financial stability',
                    'icon': 'portfolio'
                })
        
        return insights
    
    def _analyze_cash_flow(self, transactions: Dict, financial_context: Dict) -> List[Dict]:
        """Analyze cash flow patterns"""
        insights = []
        
        # Analyze income vs expenses
        monthly_income = financial_context.get('monthly_income', 50000)
        monthly_expenses = transactions.get('monthly_expenses', 0)
        
        if monthly_expenses > 0:
            savings_ratio = ((monthly_income - monthly_expenses) / monthly_income) * 100 if monthly_income > 0 else 0
            
            if savings_ratio < 10:
                insights.append({
                    'title': 'Low Savings Rate',
                    'priority': 'High Priority',
                    'description': f'Your savings rate is {savings_ratio:.1f}%. Aim for 20-30% to build wealth effectively.',
                    'action': 'Create budget plan',
                    'save': 'Build wealth',
                    'icon': 'spending'
                })
            elif savings_ratio > 40:
                insights.append({
                    'title': 'Excellent Savings Rate',
                    'priority': 'Opportunity',
                    'description': f'Your savings rate is {savings_ratio:.1f}%. Consider investing excess funds for better returns.',
                    'action': 'Explore investment options',
                    'save': 'Higher returns',
                    'icon': 'opportunity'
                })
        
        return insights
    
    def calculate_health_score(self, financial_data: Dict, user_goals: List[Dict] = None) -> Dict:
        """Calculate comprehensive financial health score"""
        logging.info("🎯 Custom Agent: Calculating health score")
        
        try:
            # Prepare financial context
            financial_context = self._prepare_comprehensive_context(financial_data, {'goals': user_goals})
            
            # Calculate health score based on multiple metrics
            metrics = financial_context.get('metrics', {})
            portfolio = financial_context.get('portfolio', {})
            transactions = financial_context.get('transactions', {})
            
            # 1. Emergency Fund Score (0-100)
            emergency_ratio = metrics.get('emergency_fund_ratio', 0)
            emergency_score = min(100, emergency_ratio)
            
            # 2. Debt Management Score (0-100)
            debt_ratio = metrics.get('debt_to_income_ratio', 0)
            debt_score = max(0, 100 - debt_ratio)
            
            # 3. Investment Allocation Score (0-100)
            investment_ratio = metrics.get('investment_ratio', 0)
            investment_score = min(100, investment_ratio * 2)  # Scale up for better scoring
            
            # 4. Net Worth Score (0-100)
            net_worth = metrics.get('net_worth', 0)
            net_worth_score = min(100, max(0, (net_worth / 1000000) * 100))  # Scale based on 10L net worth
            
            # 5. Cash Flow Score (0-100) - NEW CATEGORY
            monthly_income = financial_context.get('monthly_income', 50000)
            monthly_expenses = transactions.get('monthly_expenses', 0)
            if monthly_expenses > 0 and monthly_income > 0:
                savings_ratio = ((monthly_income - monthly_expenses) / monthly_income) * 100
                cash_flow_score = min(100, max(0, savings_ratio * 2))  # Scale up savings ratio
            else:
                cash_flow_score = 50  # Default if no data
            
            # 6. Portfolio Diversification Score (0-100) - NEW CATEGORY
            equity_allocation = portfolio.get('equity_allocation', 0)
            debt_allocation = portfolio.get('debt_allocation', 0)
            cash_allocation = portfolio.get('cash_allocation', 0)
            
            # Ideal allocation: 60% equity, 30% debt, 10% cash
            ideal_equity = 60
            ideal_debt = 30
            ideal_cash = 10
            
            equity_deviation = abs(equity_allocation - ideal_equity)
            debt_deviation = abs(debt_allocation - ideal_debt)
            cash_deviation = abs(cash_allocation - ideal_cash)
            
            total_deviation = equity_deviation + debt_deviation + cash_deviation
            diversification_score = max(0, 100 - total_deviation)
            
            # Calculate overall score (average of all 6 categories)
            overall_score = (emergency_score + debt_score + investment_score + 
                           net_worth_score + cash_flow_score + diversification_score) / 6
            
            # Determine category
            if overall_score >= 80:
                category = "Excellent"
            elif overall_score >= 60:
                category = "Good"
            elif overall_score >= 40:
                category = "Fair"
            else:
                category = "Poor"
            
            # Create comprehensive breakdown with 6 categories
            breakdown = {
                "Emergency Fund": round(emergency_score, 1),
                "Debt Management": round(debt_score, 1),
                "Investment Allocation": round(investment_score, 1),
                "Net Worth": round(net_worth_score, 1),
                "Cash Flow": round(cash_flow_score, 1),
                "Portfolio Diversification": round(diversification_score, 1)
            }
            
            # Generate strengths
            strengths = []
            if emergency_score >= 70:
                strengths.append("Strong emergency fund coverage")
            if debt_score >= 70:
                strengths.append("Good debt management")
            if investment_score >= 60:
                strengths.append("Healthy investment allocation")
            if net_worth_score >= 50:
                strengths.append("Positive net worth")
            if cash_flow_score >= 60:
                strengths.append("Good savings rate")
            if diversification_score >= 70:
                strengths.append("Well-diversified portfolio")
            
            # Generate weaknesses
            weaknesses = []
            if emergency_score < 50:
                weaknesses.append("Insufficient emergency fund")
            if debt_score < 50:
                weaknesses.append("High debt-to-income ratio")
            if investment_score < 40:
                weaknesses.append("Low investment allocation")
            if net_worth_score < 30:
                weaknesses.append("Low net worth")
            if cash_flow_score < 40:
                weaknesses.append("Low savings rate")
            if diversification_score < 50:
                weaknesses.append("Poor portfolio diversification")
            
            # Generate recommendations
            recommendations = []
            if emergency_score < 70:
                recommendations.append("Build emergency fund to cover 6 months of expenses")
            if debt_score < 70:
                recommendations.append("Focus on debt reduction and avoid new debt")
            if investment_score < 60:
                recommendations.append("Increase investment allocation for better returns")
            if net_worth_score < 50:
                recommendations.append("Focus on wealth building through savings and investments")
            if cash_flow_score < 50:
                recommendations.append("Improve savings rate by reducing expenses or increasing income")
            if diversification_score < 60:
                recommendations.append("Rebalance portfolio for better diversification")
            
            # Overall analysis
            overall_analysis = f"Your financial health score is {overall_score:.1f}/100, placing you in the '{category}' category. "
            overall_analysis += f"Your emergency fund covers {emergency_ratio:.1f}% of recommended expenses, "
            overall_analysis += f"debt-to-income ratio is {debt_ratio:.1f}%, "
            overall_analysis += f"investment allocation is {investment_ratio:.1f}% of net worth, "
            overall_analysis += f"and your current net worth is ₹{net_worth:,.0f}. "
            overall_analysis += f"Your portfolio diversification score is {diversification_score:.1f}/100."
            
            logging.info(f"✅ Custom Agent: Calculated health score: {overall_score:.1f}")
            return {
                'score': round(overall_score, 1),
                'category': category,
                'breakdown': breakdown,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'recommendations': recommendations,
                'overall_analysis': overall_analysis
            }
            
        except Exception as e:
            logging.error(f"❌ Custom Agent: Error calculating health score: {e}")
            logging.error(f"❌ Custom Agent: Exception details: {str(e)}")
            
            # Enhanced fallback with more categories
            return {
                'score': 50.0,
                'category': 'Fair',
                'breakdown': {
                    'Emergency Fund': 50.0,
                    'Debt Management': 50.0,
                    'Investment Allocation': 50.0,
                    'Net Worth': 50.0,
                    'Cash Flow': 50.0,
                    'Portfolio Diversification': 50.0
                },
                'strengths': ['Basic financial foundation'],
                'weaknesses': ['Limited financial data available for detailed analysis'],
                'recommendations': ['Provide more financial data for comprehensive analysis'],
                'overall_analysis': 'Unable to calculate detailed metrics due to limited data. Please connect more financial accounts for better analysis.'
            }
    
    def analyze_financial_query(self, user_message: str, financial_data: Dict, 
                              chat_history: List[Dict] = None, user_profile: Dict = None) -> Dict:
        """
        Main entry point for custom financial analysis - ADK Compatible
        Maintains backward compatibility while using ADK framework
        """
        # Use ADK-compliant analysis
        adk_result = self.analyze_financial_query_adk(user_message, financial_data, chat_history, user_profile)
        
        # Convert ADK response to legacy format for backward compatibility
        legacy_response = {
            'response': adk_result.get('response', ''),
            'analysis_type': adk_result.get('analysis_type', 'general'),
            'recommendations': adk_result.get('recommendations', []),
            'insights': adk_result.get('insights', []),
            'metrics': adk_result.get('metrics', {}),
            'confidence_score': adk_result.get('confidence_score', 0.0),
            'tools_used': adk_result.get('tools_used', []),
            'adk_compliant': True
        }
        
        return legacy_response
    
    def get_adk_info(self) -> Dict:
        """Get ADK agent information"""
        return {
            "name": "Custom Financial Advisor Agent",
            "version": "1.0",
            "description": "Advanced AI-powered financial analysis with Indian context",
            "capabilities": list(self.capabilities.keys()),
            "tools": self.get_tools(),
            "schema": self.get_schema(),
            "adk_compliant": True
        }
    
    def validate_adk_compliance(self) -> Dict:
        """Validate ADK compliance"""
        compliance_report = {
            "adk_compliant": True,
            "missing_features": [],
            "tool_definitions": len(self.tools),
            "response_schema": bool(self.response_schema),
            "function_calling": True,
            "error_handling": True
        }
        
        # Check for required ADK features
        required_methods = ['get_tools', 'get_schema', 'call_function', 'analyze_financial_query_adk']
        for method in required_methods:
            if not hasattr(self, method):
                compliance_report["adk_compliant"] = False
                compliance_report["missing_features"].append(f"method: {method}")
        
        return compliance_report
    
    def _prepare_comprehensive_context(self, financial_data: Dict, user_profile: Dict = None) -> Dict:
        """Prepare comprehensive financial context for analysis"""
        try:
            # Extract portfolio data
            portfolio = self._extract_portfolio_data(financial_data)
            
            # Extract transaction data
            transactions = self._extract_transaction_data(financial_data)
            
            # Extract credit data
            credit = self._extract_credit_data(financial_data)
            
            # Get user goals if available
            goals = []
            if user_profile:
                goals = user_profile.get('goals', [])
            
            # Calculate metrics
            metrics = {
                'net_worth': portfolio.get('net_worth', 0),
                'total_assets': portfolio.get('total_assets', 0),
                'total_liabilities': portfolio.get('total_liabilities', 0),
                'emergency_fund_ratio': portfolio.get('emergency_fund_ratio', 0),
                'debt_to_income_ratio': credit.get('debt_to_income_ratio', 0),
                'credit_score': credit.get('credit_score', 0)
            }
            
            return {
                'portfolio': portfolio,
                'transactions': transactions,
                'credit': credit,
                'goals': goals,
                'metrics': metrics,
                'profile': user_profile or {},
                'income': portfolio.get('income', 0),
                'investments': portfolio.get('investments', {}),
                'trust_rating': {}  # Will be populated by lending analysis
            }
            
        except Exception as e:
            logging.error(f"Error preparing comprehensive context: {e}")
            return {
                'portfolio': {},
                'transactions': {},
                'credit': {},
                'goals': [],
                'metrics': {},
                'profile': user_profile or {},
                'income': 0,
                'investments': {},
                'trust_rating': {}
            }
    
    def _analyze_query_intent_custom(self, user_message: str) -> Dict:
        """Analyze user query intent with confidence scoring"""
        try:
            message_lower = user_message.lower()
            
            # Define intent patterns with confidence scores
            intent_patterns = {
                'portfolio_analysis': {
                    'keywords': ['portfolio', 'allocation', 'investments', 'assets', 'stocks', 'mutual funds'],
                    'confidence': 0.9
                },
                'tax_optimization': {
                    'keywords': ['tax', '80c', '80d', 'savings', 'deduction', 'income tax'],
                    'confidence': 0.9
                },
                'debt_management': {
                    'keywords': ['debt', 'loan', 'credit card', 'emi', 'repayment', 'borrow'],
                    'confidence': 0.9
                },
                'investment_planning': {
                    'keywords': ['invest', 'sip', 'fund', 'growth', 'returns', 'investment'],
                    'confidence': 0.8
                },
                'risk_assessment': {
                    'keywords': ['risk', 'safety', 'secure', 'volatile', 'stability'],
                    'confidence': 0.8
                },
                'goal_planning': {
                    'keywords': ['goal', 'target', 'save', 'plan', 'future', 'retirement'],
                    'confidence': 0.9
                },
                'scenario_modeling': {
                    'keywords': ['what if', 'scenario', 'simulation', 'projection', 'forecast'],
                    'confidence': 0.8
                },
                'cash_flow_analysis': {
                    'keywords': ['cash flow', 'income', 'expense', 'budget', 'spending'],
                    'confidence': 0.8
                },
                'salary_analysis': {
                    'keywords': ['salary', 'income', 'payroll', 'wages', 'salary credit', 'monthly income', 'earnings'],
                    'confidence': 0.9
                },
                'lending_borrowing': {
                    'keywords': ['lend', 'borrow', 'money', 'loan', 'udhaar', 'bharosa', 'trust'],
                    'confidence': 0.9
                }
            }
            
            # Find matching intents
            matched_intents = []
            for intent_type, pattern in intent_patterns.items():
                keyword_matches = sum(1 for keyword in pattern['keywords'] if keyword in message_lower)
                if keyword_matches > 0:
                    confidence = min(pattern['confidence'] * keyword_matches / len(pattern['keywords']), 1.0)
                    matched_intents.append({
                        'type': intent_type,
                        'confidence': confidence,
                        'matches': keyword_matches
                    })
            
            # Sort by confidence and return best match
            if matched_intents:
                best_match = max(matched_intents, key=lambda x: x['confidence'])
                return {
                    'type': best_match['type'],
                    'confidence': best_match['confidence'],
                    'all_matches': matched_intents
                }
            else:
                # Default to general analysis
                return {
                    'type': 'general_financial',
                    'confidence': 0.5,
                    'all_matches': []
                }
                
        except Exception as e:
            logging.error(f"Error analyzing query intent: {e}")
            return {
                'type': 'general_financial',
                'confidence': 0.3,
                'all_matches': []
            }
    
    def _analyze_salary_patterns(self, transactions: Dict, financial_context: Dict) -> List[Dict]:
        """Analyze salary credit patterns and provide insights"""
        insights = []
        
        try:
            # Extract salary-related transactions
            salary_transactions = []
            monthly_income = financial_context.get('monthly_income', 0)
            
            if 'bank_transactions' in transactions:
                for transaction in transactions['bank_transactions']:
                    description = transaction.get('description', '').upper()  # Convert to uppercase for exact matching
                    amount = transaction.get('amount', 0)
                    
                    # Primary detection: Look for exact "SALARY CREDIT" pattern
                    if "SALARY CREDIT" in description and amount > 0:
                        salary_transactions.append({
                            'amount': amount,
                            'description': transaction.get('description', ''),
                            'date': transaction.get('date', ''),
                            'type': 'salary_credit'
                        })
                        logging.info(f"✅ Detected SALARY CREDIT: ₹{amount:,.0f} on {transaction.get('date', '')}")
                    
                    # Secondary detection: Look for other salary-related keywords
                    elif amount > 0:
                        salary_keywords = ['SALARY', 'PAYROLL', 'WAGES', 'INCOME', 'STIPEND']
                        if any(keyword in description for keyword in salary_keywords):
                            salary_transactions.append({
                                'amount': amount,
                                'description': transaction.get('description', ''),
                                'date': transaction.get('date', ''),
                                'type': 'salary_related'
                            })
                            logging.info(f"✅ Detected salary-related transaction: ₹{amount:,.0f} - {description}")
            
            if salary_transactions:
                # Analyze salary patterns
                total_salary = sum(t['amount'] for t in salary_transactions)
                avg_salary = total_salary / len(salary_transactions)
                
                # Categorize by type
                salary_credits = [t for t in salary_transactions if t['type'] == 'salary_credit']
                salary_related = [t for t in salary_transactions if t['type'] == 'salary_related']
                
                # Salary consistency analysis
                salary_variance = sum(abs(t['amount'] - avg_salary) for t in salary_transactions) / len(salary_transactions)
                consistency_ratio = (avg_salary - salary_variance) / avg_salary if avg_salary > 0 else 0
                
                # Enhanced salary analysis insights
                if salary_credits:
                    insights.append({
                        'title': 'Salary Credit Pattern Detected',
                        'priority': 'Informational',
                        'description': f'Found {len(salary_credits)} salary credit transactions. Average salary: ₹{avg_salary:,.0f}. Consistency: {consistency_ratio*100:.1f}%.',
                        'action': 'View salary trends',
                        'save': 'Financial planning',
                        'icon': 'income'
                    })
                
                # Salary growth analysis (if multiple months of data)
                if len(salary_transactions) >= 2:
                    # Sort by date for chronological analysis
                    sorted_transactions = sorted(salary_transactions, key=lambda x: x['date'])
                    recent_salary = sorted_transactions[-1]['amount']
                    older_salary = sorted_transactions[0]['amount']
                    growth_rate = ((recent_salary - older_salary) / older_salary * 100) if older_salary > 0 else 0
                    
                    if growth_rate > 5:
                        insights.append({
                            'title': 'Salary Growth Detected',
                            'priority': 'Opportunity',
                            'description': f'Your salary has increased by {growth_rate:.1f}% recently (₹{older_salary:,.0f} → ₹{recent_salary:,.0f}). Consider increasing your investments proportionally.',
                            'action': 'Adjust investment allocation',
                            'save': 'Maintain savings rate',
                            'icon': 'opportunity'
                        })
                    elif growth_rate < -5:
                        insights.append({
                            'title': 'Salary Reduction Alert',
                            'priority': 'High Priority',
                            'description': f'Your salary has decreased by {abs(growth_rate):.1f}% recently (₹{older_salary:,.0f} → ₹{recent_salary:,.0f}). Review your budget and consider reducing expenses.',
                            'action': 'Review budget',
                            'save': 'Maintain financial stability',
                            'icon': 'alert'
                        })
                    else:
                        insights.append({
                            'title': 'Stable Salary Pattern',
                            'priority': 'Informational',
                            'description': f'Your salary has remained stable with {growth_rate:.1f}% change. Good for consistent financial planning.',
                            'action': 'Continue current strategy',
                            'save': 'Financial stability',
                            'icon': 'income'
                        })
                
                # Salary timing analysis
                salary_dates = [t['date'] for t in salary_transactions]
                if salary_dates:
                    # Analyze salary timing patterns
                    insights.append({
                        'title': 'Salary Credit Analysis',
                        'priority': 'Informational',
                        'description': f'Your average monthly salary is ₹{avg_salary:,.0f}. Salary consistency is {consistency_ratio*100:.1f}%. Total salary transactions: {len(salary_transactions)}.',
                        'action': 'View salary trends',
                        'save': 'Financial planning',
                        'icon': 'income'
                    })
                
                # Salary vs expenses analysis
                monthly_expenses = transactions.get('monthly_expenses', 0)
                if monthly_expenses > 0:
                    salary_to_expense_ratio = (avg_salary / monthly_expenses) * 100
                    
                    if salary_to_expense_ratio < 120:
                        insights.append({
                            'title': 'Low Salary-to-Expense Ratio',
                            'priority': 'High Priority',
                            'description': f'Your salary covers only {salary_to_expense_ratio:.1f}% of your expenses (₹{avg_salary:,.0f} salary vs ₹{monthly_expenses:,.0f} expenses). Consider reducing expenses or seeking additional income.',
                            'action': 'Review expenses',
                            'save': 'Financial stability',
                            'icon': 'alert'
                        })
                    elif salary_to_expense_ratio > 200:
                        insights.append({
                            'title': 'Excellent Salary-to-Expense Ratio',
                            'priority': 'Opportunity',
                            'description': f'Your salary covers {salary_to_expense_ratio:.1f}% of expenses (₹{avg_salary:,.0f} salary vs ₹{monthly_expenses:,.0f} expenses). Great opportunity to increase investments.',
                            'action': 'Increase investments',
                            'save': 'Build wealth faster',
                            'icon': 'opportunity'
                        })
                    else:
                        insights.append({
                            'title': 'Healthy Salary-to-Expense Ratio',
                            'priority': 'Informational',
                            'description': f'Your salary covers {salary_to_expense_ratio:.1f}% of expenses. This is a healthy ratio for financial stability.',
                            'action': 'Maintain current balance',
                            'save': 'Financial stability',
                            'icon': 'income'
                        })
                
                # Salary investment opportunity
                if avg_salary > 50000:  # If salary is above 50k
                    potential_investment = avg_salary * 0.3  # 30% of salary
                    insights.append({
                        'title': 'Salary Investment Opportunity',
                        'priority': 'Medium Priority',
                        'description': f'Consider investing ₹{potential_investment:,.0f} (30% of salary) monthly for better wealth building. This could grow to ₹{potential_investment * 12 * 10:,.0f} in 10 years.',
                        'action': 'Set up SIP',
                        'save': 'Long-term wealth',
                        'icon': 'investment'
                    })
                
                # Salary frequency analysis
                if len(salary_transactions) >= 3:
                    # Analyze salary frequency (monthly, bi-weekly, etc.)
                    insights.append({
                        'title': 'Salary Frequency Analysis',
                        'priority': 'Informational',
                        'description': f'Detected {len(salary_transactions)} salary transactions. Average frequency: {len(salary_transactions)} transactions per period analyzed.',
                        'action': 'Review salary patterns',
                        'save': 'Better financial planning',
                        'icon': 'income'
                    })
            
            # If no salary data found, add generic income insight
            else:
                insights.append({
                    'title': 'Salary Pattern Not Detected',
                    'priority': 'Medium Priority',
                    'description': 'No "SALARY CREDIT" or salary-related transactions found. Connect your salary account or ensure salary credits are properly labeled for better analysis.',
                    'action': 'Connect salary account',
                    'save': 'Better insights',
                    'icon': 'income'
                })
                
        except Exception as e:
            logging.error(f"Error analyzing salary patterns: {e}")
            insights.append({
                'title': 'Salary Analysis Error',
                'priority': 'Informational',
                'description': 'Unable to analyze salary patterns at this time. Please try again later.',
                'action': 'Retry analysis',
                'save': '',
                'icon': 'info'
            })
        
        return insights
    
    def _salary_analysis(self, user_message: str, financial_context: Dict) -> Dict:
        """Analyze salary patterns and provide salary-related insights"""
        try:
            transactions = financial_context.get('transactions', {})
            
            # Get salary insights
            salary_insights = self._analyze_salary_patterns(transactions, financial_context)
            
            # Generate comprehensive salary analysis
            analysis_text = "Based on your salary patterns, here's my analysis:\n\n"
            
            if salary_insights:
                for insight in salary_insights:
                    analysis_text += f"• {insight['title']}: {insight['description']}\n"
                    analysis_text += f"  Action: {insight['action']}\n"
                    analysis_text += f"  Potential Savings: {insight['save']}\n\n"
            else:
                analysis_text += "No salary patterns detected in your transactions. Consider connecting your salary account for better analysis.\n\n"
            
            # Add salary-specific recommendations
            recommendations = []
            for insight in salary_insights:
                recommendations.append({
                    'title': insight['title'],
                    'description': insight['description'],
                    'priority': insight['priority'],
                    'action': insight['action']
                })
            
            return {
                'text': analysis_text,
                'recommendations': recommendations,
                'analysis_type': 'salary_analysis',
                'insights': salary_insights
            }
            
        except Exception as e:
            logging.error(f"Error in salary analysis: {e}")
            return {
                'text': "I'm having trouble analyzing your salary patterns right now. Please try again later.",
                'recommendations': [],
                'analysis_type': 'salary_analysis',
                'insights': []
            }