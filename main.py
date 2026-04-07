from memory import ConversationMemory
from brain import JarvisBrain
from stt import JarvisEars
from tts import JarvisMouth

SYSTEM_PROMPT = """
You are JARVIS, a highly intelligent and concise AI assistant.
Always keep your verbal responses brief and to the point.
"""

def initialize_jarvis():
    """
    Boots up all JARVIS subsyatems and returns the initialized objects
    """
    print("[System] Booting up JARVIS protocols...")

    # 1. Initialize Memory with the core persona
    memory = ConversationMemory(
        system_prompt=SYSTEM_PROMPT,
        max_turns=8
    )

    # 2. Initialize the remaining modules
    brain = JarvisBrain(model_name="llama3.1")
    ears = JarvisEars()
    mouth = JarvisMouth()

    print("[System] All modules loaded successfully.")
    return memory, brain, ears, mouth

def run_jarvis():
    """
    The main continous loop for JARVIS
    """

    # Bring the systems online
    memory, brain, ears, mouth = initialize_jarvis()

    mouth.speak("All systems online. Good to see you, sir.")

    while True:
        try:
            #LISTEN
            user_text = ears.listen()

            if not user_text:
                continue

            print(f"\n[You]: {user_text}")

            # --- Hardcoded Exit Commands ---
            if "sleep jarvis" in user_text.lower() or "shut down" in user_text.lower() or "exit" in user_text.lower():
                mouth.speak("Powering down. Goodbye, sir.")
                break

            # 2. THINK (Brain + Memory)
            print("[JARVIS is thinking...]")
            response_text = brain.think(user_text, memory)

            # 3. SPEAK (Mouth)
            mouth.speak(response_text)

        except KeyboardInterrupt:
            # Catches CTRL+C in the terminal for a clean exit
            print("\n[System] Manual shutdown initiated.")
            break
        except Exception as e:
            # Prevents the whole program from crashing if Ollama or Coqui throws a random error
            print(f"\n[System Error]: {e}")
            mouth.speak("Pardon me sir, but I seem to have encountered a system error.")

if __name__ == "__main__":
    run_jarvis()