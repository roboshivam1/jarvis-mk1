import requests
from listener import record_audio, transcribe_audio
from speaker import speak
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

system_prompt = """
You are JARVIS, a smart, efficient, slightly witty AI assistant of Shivam Kapoor(address him as 'sir')
- Keep responses concise
- Be helpful and direct
- Avoid long explanations unless asked
- Do not make things up yourself, only speak with data given to you, no false information. 
"""

conversation = []
summary_memory = ""

MAX_TURNS = 8

def build_prompt(user_input): #This function makes your prompts (bruh)
    global conversation, summary_memory

    prompt = system_prompt + "\n\n"

    if summary_memory:
        prompt += f"Memory Summary:\n{summary_memory}\n\n"
    
    prompt += "Recent Conversation:\n"

    for role, text in conversation:
        prompt += f"{role}: {text}\n"
    
    prompt += f"User: {user_input}\nJARVIS:"

    return prompt

def ask_jarvis(prompt): #posts built prompt to ollama model and returns reply
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"].strip()

def update_conversation(user_input, reply): #just appends user input and jarvis output in each turn and trims last turn messages.  
    global conversation

    conversation.append(("User", user_input))
    conversation.append(("JARVIS", reply))

    #we keep max_turns*2 entries (user + jarvis)
    if len(conversation) > MAX_TURNS*2:
        conversation = conversation[-MAX_TURNS * 2:]

def summarize_memory(): #summarizes older memory to reduce tokens. 
    global summary_memory, conversation

    if not summary_memory:
        return
    
    text_to_summarize = summary_memory + "\n"

    for role, text in conversation:
        text_to_summarize += f"{role}: {text}"
    
    prompt = f"""
Summarize the following conversation into short key points for memory.
Keep only important context.

{text_to_summarize}

Summary:
"""
    
    summary_memory = ask_jarvis(prompt)
    conversation.clear()

if __name__=="__main__": #MAIN LOOP
    print("JARVIS is online. Type 'exit' to quit.\n")

    while True:
        print("Press SPACE to speak...")
        audio_file = record_audio()
        user_input = transcribe_audio(audio_file)

        if not user_input.strip():
            print("Didn't catch that.")
            continue

        print("You:", user_input)

        if user_input.lower() == "exit":
            print("JARVIS: Goodbye!")
            break

        prompt = build_prompt(user_input)

        reply = ask_jarvis(prompt)

        print("JARVIS:", reply, "\n")
        reply = reply.replace("\n", " ")
        speak(reply)

        update_conversation(user_input, reply)

        if len(conversation) >= MAX_TURNS*2:
            print("(Summarizing memory...)")
            summarize_memory()
        
        os.remove(audio_file)