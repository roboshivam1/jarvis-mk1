from TTS.api import TTS
import os

print("Loading speech synthesis model...")
tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)
print("Speech synthesis model loaded.")

SPEAKER = "p230"

def speak(text):
    if not text.strip():
        return

    print("🔊 JARVIS speaking...")

    filename = "output.wav"

    # Generate speech
    tts.tts_to_file(text=text, speaker=SPEAKER, file_path=filename, speed=1.0)

    # Play audio (Mac)
    os.system(f"afplay {filename}")

    # Optional: delete file after playing
    os.remove(filename)