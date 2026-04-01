import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def classify_intent(user_input):
    prompt = f"""
Classify the user's intent.

Respond ONLY with one word:
- "command"
- "chat"

Examples:

Input: open youtube
Output: command

Input: search best laptops
Output: command

Input: how are you
Output: chat

Input: explain AI
Output: chat

Now classify:
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

    return response.json()["response"].strip().lower()