from flask import Flask, jsonify, request
import os
import fi_money_mcp
import gemini

app = Flask(__name__)

@app.route('/api/user/recommendations', methods=['GET'])
def get_recommendations():
    # In a real application, the user token would be passed in the request
    # headers or body.
    user_token = 'mock-user-token'

    try:
        financial_data = fi_money_mcp.get_financial_data(user_token)
        recommendations = gemini.get_gemini_recommendations(financial_data)
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to get financial recommendations.'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
