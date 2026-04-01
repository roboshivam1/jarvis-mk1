import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def get_web_command(user_input):
    prompt = f"""
You are a command parser.

Convert the user request into a JSON format.

ONLY respond in this format:
{{
    "action": "open_url" or "google_search",
    "value": "URL or search query"
}}

Examples:

Input: open youtube
Output: {{"action": "open_url", "value": "https://youtube.com"}}

Input: search AI tutorials
Output: {{"action": "google_search", "value": "AI tutorials"}}

Input: open instagram
Output: {{"action": "open_url", "value": "https://instagram.com"}}

Now process:
Input: {user_input}
Output:
"""
    
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    text = response.json()["response"].strip()

    return text

def parse_ai_command(response_text):
    try:
        return json.loads(response_text)
    except:
        return None
