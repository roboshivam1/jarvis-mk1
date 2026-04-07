import sounddevice as sd
import numpy as np
import wave
import time
import os
from pynput import keyboard
from faster_whisper import WhisperModel

class JarvisEars:
    def __init__(self, model_size: str = "base.en"):
        """
        Initializes the Push-to-Talk engine using faster_whisper.
        """
        print("[System] Waking up JARVIS's ears (Push-to-Talk enabled)...")
        self.model = WhisperModel(model_size, device="auto", compute_type="int8")
        
        # Whisper requires audio to be recorded at exactly 16000 Hz
        self.sample_rate = 16000 
        self.is_recording = False
        self.audio_data = []

    def listen(self) -> str:
        """
        Waits for the Right Shift key to be held down, records audio, 
        and transcribes it when the key is released.
        """
        print("\n[System] Press and HOLD the 'Right Shift' key to speak...")
        self.is_recording = False
        self.audio_data = []

        # --- Key Press Logic ---
        def on_press(key):
            # When Right Shift is pressed down, start recording
            if key == keyboard.Key.shift_r and not self.is_recording:
                self.is_recording = True
                print("\r[JARVIS is recording... Release 'Right Shift' to stop]", end="")

        def on_release(key):
            # When Right Shift is let go, stop recording and kill the listener
            if key == keyboard.Key.shift_r:
                self.is_recording = False
                return False 

        # --- Audio Recording Logic ---
        # We start the keyboard listener
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            # We open an audio stream
            stream = sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16')
            with stream:
                # Keep running as long as the listener hasn't been killed
                while listener.running:
                    if self.is_recording:
                        # Grab 1024 frames of audio and add to our list
                        chunk, _ = stream.read(1024)
                        self.audio_data.append(chunk)
                    else:
                        # Sleep briefly so we don't max out the CPU while waiting
                        time.sleep(0.05)

        # If you just tapped the key and no audio was recorded, return nothing
        if not self.audio_data:
            return ""

        print("\n[Transcribing...]")
        
        # Flatten the audio chunks into one continuous array
        audio_np = np.concatenate(self.audio_data, axis=0)
        
        # Save the raw audio to a temporary .wav file
        temp_file = "temp_voice.wav"
        with wave.open(temp_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 2 bytes for int16 format
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_np.tobytes())

        # Transcribe using faster_whisper
        segments, _ = self.model.transcribe(temp_file, beam_size=5)
        transcription = "".join([segment.text for segment in segments])

        # Clean up the audio file
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return transcription.strip()