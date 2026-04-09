from TTS.api import TTS
import os
import subprocess
import threading
import queue
import uuid
import glob

class JarvisMouth:
    def __init__(self, model_name: str = "tts_models/en/vctk/vits"):
        """
        Initializes the text to speech engine using coqui tts and starts the playback thread.
        """
        print("[System] Warming up JARVIS's voice...")
        self.tts = TTS(model_name=model_name, progress_bar=False, gpu=False)
        
        # Clean up any leftover audio files if the program previously crashed
        for leftover_file in glob.glob("temp_response_*.wav"):
            try:
                os.remove(leftover_file)
            except OSError:
                pass
            
        # The bucket to hold audio file paths waiting to be played
        self.playback_queue = queue.Queue()
        
        # Start the background 'Speaker' thread
        self.speaker_thread = threading.Thread(target=self._audio_player_worker, daemon=True)
        self.speaker_thread.start()

    def _audio_player_worker(self):
        """
        Background thread that constantly checks the queue and plays audio gaplessly.
        """
        while True:
            file_path = self.playback_queue.get()
            
            if file_path is None: # Kill signal
                break 
                
            # Play the audio using Mac's afplay (blocks only this thread until finished)
            subprocess.run(["afplay", file_path])
            
            # Immediately delete the file after playing to save space
            if os.path.exists(file_path):
                os.remove(file_path)
                
            self.playback_queue.task_done()

    def speak(self, text: str, speaker_id: str = "p230") -> None:
        """
        Synthesizes the text into an audio file and drops it into the playback queue.
        This function returns very quickly, allowing the brain to keep working.
        """
        if not text.strip():
            return
            
        # 1. Create a unique filename for this specific sentence
        # We must do this so we don't overwrite a file that is currently playing!
        file_path = f"temp_response_{uuid.uuid4().hex}.wav"
        
        # 2. Synthesize the audio to the file
        self.tts.tts_to_file(text=text, file_path=file_path, speaker=speaker_id)
        
        # 3. Drop it in the queue for the Speaker thread to pick up and play
        self.playback_queue.put(file_path)

    def wait_until_done(self):
        """
        Blocks the main program until all queued audio has finished playing.
        """
        self.playback_queue.join()