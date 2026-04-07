from faster_whisper import WhisperModel
import speech_recognition as sr
import os

class JarvisEars:
    def __init__(self, model_size: str = "base.en"):
        """
        Initializing JARVIS ears
        """
        print("[System] Waking up JARVIS's ears...")
        # device="auto" allows CPU/GPU optimally
        # compute_type="int8" keeps memory usage very low
        self.model = WhisperModel(model_size, device="auto", compute_type="int8")

        # We use SpeechRecognition purely to handle the microphone logic easily
        self.recognizer = sr.Recognizer()

    def listen(self) -> str:
        """
        Listens to the microphone and returns the transcribed text.
        """

        with sr.Microphone() as source:
            print("\n[JARVIS is listening... Speak now]")
            # Adjust for ambient noise so he doesn't record static
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Record the audio until you stop speaking
            audio = self.recognizer.listen(source)
            
            # Save the raw audio to a temporary file
            temp_file = "temp_voice.wav"
            with open(temp_file, "wb") as f:
                f.write(audio.get_wav_data())
                
        print("[Transcribing...]")
        # Transcribe the temporary file
        segments, _ = self.model.transcribe(temp_file, beam_size=5)
        
        # Combine all the transcribed text segments into one string
        transcription = "".join([segment.text for segment in segments])
        
        # Clean up the temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return transcription.strip()

