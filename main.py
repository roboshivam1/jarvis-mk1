import threading
import queue
from memory import ConversationMemory
from brain import JarvisBrain
from stt import JarvisEars
from tts import JarvisMouth
from datetime import date

today_date = date.today()

SYSTEM_PROMPT = (
        "You are JARVIS, a highly intelligent and capable AI assistant. "
        "You have been granted system-level access to the user's Mac via Python tools. "
        f"Current Date: {today_date.strftime} 'YYYY-MM-DD'"
        "CRITICAL RULES: "
        "1. ONLY use tools if the user EXPLICITLY asks for them. Do not use tools wastefully."
        "2. If a tool successfully executes an action (like playing music, changing volume, or opening apps), "
        "DO NOT apologize or claim you cannot perform the action. "
        "3. Acknowledge the success naturally based on the tool's result (e.g., 'Playing the track for you now, sir.'). "
        "4. Keep your verbal responses brief and conversational. Also I would love witty and creative responses from your side."
    )

def initialize_jarvis():
    """
    Boots up all JARVIS subsystems and returns the initialized objects
    """
    print("[System] Booting up JARVIS protocols...")

    # 1. Initialize Memory with the core persona
    memory = ConversationMemory(
        system_prompt=SYSTEM_PROMPT,
        max_turns=8
    )

    # 2. Initialize the remaining modules
    brain = JarvisBrain()
    ears = JarvisEars()
    mouth = JarvisMouth()

    print("[System] All modules loaded successfully.")
    return memory, brain, ears, mouth

def print_banner():
    banner = r"""
    /$$$$$  /$$$$$$  /$$$$$$$  /$$    /$$ /$$$$$$  /$$$$$$ 
   |__  $$ /$$__  $$| $$__  $$| $$   | $$|_  $$_/ /$$__  $$
      | $$| $$  \ $$| $$  \ $$| $$   | $$  | $$  | $$  \__/
      | $$| $$$$$$$$| $$$$$$$/|  $$ / $$/  | $$  |  $$$$$$ 
 /$$  | $$| $$__  $$| $$__  $$ \  $$ $$/   | $$   \____  $$
| $$  | $$| $$  | $$| $$  \ $$  \  $$$/    | $$   /$$  \ $$
|  $$$$$$/| $$  | $$| $$  | $$   \  $/    /$$$$$$|  $$$$$$/
 \______/ |__/  |__/|__/  |__/    \_/    |______/ \______/ 
                                             
    =================================
    [ J.A.R.V.I.S. - MARK 1 ONLINE ]
    =================================
    """
    # Using 'cyan' or 'blue' ANSI codes to make it look "techy"
    print("\033[96m" + banner + "\033[0m")

def run_jarvis():
    print_banner()
    memory, brain, ears, mouth = initialize_jarvis()
    
    mouth.speak("All systems online. Good to see you, sir.")
    mouth.wait_until_done() # Ensure the greeting finishes before opening ears
    
    while True:
        try:
            # 1. Listen for user input (Push-to-Talk via ears.py)
            user_text = ears.listen()
            if not user_text: continue
                
            print(f"\n[You]: {user_text}")
            
            # Check for shutdown commands
            if "sleep jarvis" in user_text.lower() or "shut down" in user_text.lower():
                mouth.speak("Powering down. Goodbye, sir.")
                mouth.wait_until_done() # Let him finish his goodbye
                break
            
            print("[JARVIS]: ", end="", flush=True)

            # --- THE NEW STREAMING PIPELINE ---
            audio_queue = queue.Queue()

            # Background thread function: Generate text and push sentences to the queue
            def think_and_queue():
                try:
                    for sentence in brain.think(user_text, memory):
                        audio_queue.put(sentence)
                except Exception as e:
                    print(f"\n[Brain Error]: {e}")
                finally:
                    # Always send a 'None' signal so the mouth knows when to stop waiting
                    audio_queue.put(None)

            # Start the brain thinking in the background
            thinking_thread = threading.Thread(target=think_and_queue)
            thinking_thread.start()

            # The main thread (The Mouth) reads from the queue instantly
            while True:
                sentence = audio_queue.get()
                
                if sentence is None:  # Brain is completely finished generating text
                    break
                    
                # Print the sentence to the terminal and queue it for synthesis
                print(f"{sentence} ", end="", flush=True)
                mouth.speak(sentence)

            # Wait for all background audio to actually finish playing before listening again
            mouth.wait_until_done()

            print() # Move to a clean line for the next conversation turn

        except Exception as e:
            # Prevents the whole program from crashing if Ollama or Coqui throws a random error
            print(f"\n[System Error]: {e}")
            mouth.speak("Pardon me sir, but I seem to have encountered a system error.")
            mouth.wait_until_done()
            

if __name__ == "__main__":
    run_jarvis()