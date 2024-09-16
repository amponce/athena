import whisper
import sounddevice as sd
from ..utils.logger import logger
from ..config import Config
import time
import threading
import torch

class SpeechRecognizer:
    def __init__(self, config: Config):
        self.config = config
        logger.info("Loading Whisper model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model("medium.en").to(self.device)
        self.sample_rate = 16000
        logger.info(f"Whisper model loaded successfully on {self.device}.")

    def get_audio_input(self):
        logger.info("Listening for speech...")
        try:
            audio = sd.rec(int(self.config.SPEECH_RECOGNITION_TIMEOUT * self.sample_rate),
                           samplerate=self.sample_rate, channels=1)
            sd.wait()
            logger.info("Audio captured, processing...")
            return self.transcribe_with_timeout(audio)
        except Exception as e:
            logger.error(f"Error capturing audio: {e}")
            return None

    def transcribe_audio(self, audio):
        try:
            logger.info("Attempting to transcribe audio...")
            start_time = time.time()
            
            audio = whisper.pad_or_trim(audio.flatten())
            mel = whisper.log_mel_spectrogram(audio).to(self.device)
            
            logger.info("Transcribing with Whisper...")
            result = self.model.transcribe(audio, fp16=False)
            transcript = result["text"]
            
            logger.info(f"Transcription successful: {transcript}")
            
            end_time = time.time()
            logger.info(f"Transcription took {end_time - start_time:.2f} seconds")
            
            return transcript
        except Exception as e:
            logger.error(f"Error in transcribe_audio: {e}")
            return None

    def transcribe_with_timeout(self, audio, timeout=30):
        result = [None]
        
        def target():
            result[0] = self.transcribe_audio(audio)
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            logger.error("Transcription timed out")
            return None
        
        return result[0]