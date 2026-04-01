import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

system_prompt = (
        "You are JARVIS, a smart, efficient, slightly witty AI assistant."
        "Your master is Shivam Kapoor, from Jaipur, Rajasthan, India. Adress him as 'sir'"
        "Keep responses concise and helpful. You are not supposed to make up things on your own, only speak true data provided to you."
    )

"""
def ask_jarvis(prompt):
    system_prompt = (
        "You are JARVIS, a smart, efficient, slightly witty AI assistant."
        "Your master is Shivam Kapoor, from Jaipur, Rajasthan, India. Adress him as 'sir'"
        "Keep responses concise and helpful. You are not supposed to make up things on your own, only speak true data provided to you."
    )

    full_prompt = system_prompt + "\nUser: " + prompt + "\nJARVIS:"

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": full_prompt,
            "stream": False
        }
    )

    return response.json()["response"]
"""


if __name__=="__main__":
    print("JARVIS is online. Type 'exit' to quit.\n")

    conversation = ""
    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("JARVIS: Goodbye!")
            break

        conversation += f"User: {user_input}\nJARVIS:"

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3",
                "prompt": system_prompt + "\n" + conversation,
                "stream": False
            }
        )

        reply = response.json()["response"].strip()
        print("JARVIS:", reply)

        conversation += " " + reply + "\n"

        