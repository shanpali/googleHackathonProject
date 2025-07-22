from flask import Flask, jsonify, request
import os
import fi_money_mcp
import gemini
import json

app = Flask(__name__)

# Load MCP servers and prompts at startup
with open('mcp_servers.json', 'r') as f:
    mcp_servers = json.load(f)

with open('prompts.json', 'r') as f:
    prompts = json.load(f)

@app.route('/api/user/recommendations', methods=['GET'])
def get_recommendations():
    # In a real application, the user token would be passed in the request
    # headers or body.
    user_token = 'mock-user-token'

    try:
        financial_data = fi_money_mcp.get_financial_data(user_token)
        # Use the default financial_analysis prompt
        prompt_template = prompts.get('financial_analysis', '')
        recommendations = gemini.get_gemini_recommendations(financial_data, prompt_template)
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to get financial recommendations.'}), 500

@app.route('/api/mcp/prompt', methods=['POST'])
def mcp_prompt():
    data = request.get_json()
    mcp_server_id = data.get('mcp_server_id')
    prompt_id = data.get('prompt_id')
    user_token = data.get('user_token', 'mock-user-token') # Mock token

    if not mcp_server_id or not prompt_id:
        return jsonify({'error': 'mcp_server_id and prompt_id are required.'}), 400

    # Find the MCP server
    mcp_server = next((s for s in mcp_servers if s['id'] == mcp_server_id), None)
    if not mcp_server:
        return jsonify({'error': 'MCP server not found.'}), 404

    # Find the prompt
    prompt_template = prompts.get(prompt_id)
    if not prompt_template:
        return jsonify({'error': 'Prompt not found.'}), 404

    try:
        # For this example, we'll use the existing fi_money_mcp module
        # In a real application, you'd have a way to dynamically call the correct MCP server
        financial_data = fi_money_mcp.get_financial_data(user_token)

        # Get recommendations from Gemini
        recommendations = gemini.get_gemini_recommendations(financial_data, prompt_template)

        return jsonify({'recommendations': recommendations})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to process request.'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=3000)
