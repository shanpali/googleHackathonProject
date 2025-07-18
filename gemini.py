import os
import requests
import json

def get_gemini_recommendations(financial_data):
    prompt = f"As a financial advisor, analyze this data: {json.dumps(financial_data)}. Provide actionable recommendations."
    chat_history = [{"role": "user", "parts": [{"text": prompt}]}]
    payload = {"contents": chat_history}
    api_key = os.environ.get("GEMINI_API_KEY")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    try:
        response = requests.post(api_url, json=payload)
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0 and 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content'] and len(result['candidates'][0]['content']['parts']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print("Gemini API response structure unexpected:", result)
            return "Could not generate recommendations."
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "Error generating recommendations."
