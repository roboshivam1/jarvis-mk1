import threading
import queue
from memory import ConversationMemory
from brain import JarvisBrain
from stt import JarvisEars
from tts import JarvisMouth
from datetime import date
from memory_consolidator import consolidate_memory

today_date = date.today()

SYSTEM_PROMPT = (
    "You are JARVIS, a highly intelligent, witty, and capable AI assistant. "
    "You have system-level access to the user's Mac, live internet connectivity, and a long-term memory vault. "
    f"Current Date: {today_date.strftime('%Y-%m-%d')}\n\n"
    
    "--- CRITICAL TOOL OPERATING PROCEDURES ---\n"
    "1. INTENT CHECK (Action vs. Recall): You must distinguish between reading memory and taking action. \n"
    "   - RECALL: If the user asks 'What is my favorite X?' or asks about the past, ONLY use the `search_memory` tool. DO NOT trigger actions or play music.\n"
    "   - ACTION: If the user explicitly commands an action (e.g., 'Play my favorite band', 'Change volume'), use the corresponding system tool (e.g., `play_song`).\n"
    "2. NO WASTEFUL SEARCHES: Rely on your internal knowledge first. DO NOT use the web search tool for casual conversation, coding syntax, historical facts, or questions you already know the answer to. ONLY search the web for live, real-time data (like today's weather or current news).\n"
    "3. FLAWLESS EXECUTION: If a tool successfully executes an action, DO NOT apologize, hallucinate errors, or claim you lack the capability. Simply acknowledge the success smoothly based on the tool's result (e.g., 'Playing that track for you now, sir.').\n\n"
    
    "--- COMMUNICATION STYLE ---\n"
    "1. Keep your verbal responses incredibly brief, conversational, and directly to the point. No rambling.\n"
    "2. Inject polite, dry wit and creative flair into your responses. You are a sophisticated AI, not a boring robot.\n"
    "3. Never explicitly announce to the user that you are 'calling a tool' or 'searching memory'. Just seamlessly deliver the final result."
)

def initialize_jarvis():
    """
    Boots up all JARVIS subsystems and returns the initialized objects
    """
    print("[System] Booting up JARVIS protocols...")

    # 1. Initialize Memory with the core persona

    consolidate_memory()
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
    memory, brain, ears, mouth = initialize_jarvis()
    print_banner()
    
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