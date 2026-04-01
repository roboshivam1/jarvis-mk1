import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from pynput import keyboard
import time

print("Loading speech recognition model.")
model = WhisperModel("base", compute_type="int8")
print("Speech recognition model loaded.")

recording = False
has_recorded = False
audio_data = []
samplerate = 16000


def on_press(key):
    global recording, audio_data
    try:
        if key == keyboard.Key.space and not recording:  # SPACEBAR
            print("🎤 Recording...")
            recording = True
            audio_data = []
    except:
        pass


def on_release(key):
    global recording
    try:
        if key == keyboard.Key.space and recording:
            print("Recording stopped.")
            recording = False
            return False  # stop listener
    except:
        pass


def record_audio():
    global recording, audio_data

    audio_data = []
    has_recorded = False

    with keyboard.Listener(on_press=on_press, on_release=on_release):
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16') as stream:
            while True:
                if recording:
                    data, _ = stream.read(1024)
                    audio_data.append(data)
                    has_recorded = True

                elif has_recorded:
                    break

    if len(audio_data) == 0:
        print("No audio recorded!")
        return None

    audio_np = np.concatenate(audio_data, axis=0)

    import time
    filename = f"temp_{int(time.time())}.wav"
    write(filename, samplerate, audio_np)

    return filename

def transcribe_audio(file_path):
    segments, _ = model.transcribe(file_path)

    text = ""
    for segment in segments:
        text += segment.text

    return text.strip()