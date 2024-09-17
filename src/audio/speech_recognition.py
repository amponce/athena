import whisper
import sounddevice as sd
import speech_recognition as sr
from ..utils.logger import logger
from ..config import Config
import time
import threading
import torch

class SpeechRecognizer:
    def __init__(self, config: Config):
        self.config = config
        self.use_whisper = config.USE_WHISPER
        self.sample_rate = 16000

        if self.use_whisper:
            self._init_whisper()
        else:
            self._init_sr()

    def _init_whisper(self):
        logger.info("Loading Whisper model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model("medium").to(self.device)
        logger.info(f"Whisper model loaded successfully on {self.device}.")

    def _init_sr(self):
        self.recognizer = sr.Recognizer()

    def get_audio_input(self):
        return self._get_audio_whisper() if self.use_whisper else self._get_audio_sr()

    def _get_audio_whisper(self):
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

    def _get_audio_sr(self):
        time.sleep(0.5)  # Add a small delay to allow the system to stabilize after playing audio
        with sr.Microphone() as source:
            logger.info("Listening for speech...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=self.config.SPEECH_RECOGNITION_TIMEOUT, phrase_time_limit=self.config.SPEECH_RECOGNITION_PHRASE_TIME_LIMIT)
                logger.info("Audio captured, processing...")
            except sr.WaitTimeoutError:
                logger.info("No speech detected within the timeout period.")
                return None

        return self.transcribe_audio(audio)

    def transcribe_audio(self, audio):
        return self._transcribe_whisper(audio) if self.use_whisper else self._transcribe_sr(audio)

    def _transcribe_whisper(self, audio):
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

    def _transcribe_sr(self, audio):
        try:
            logger.info("Attempting to transcribe audio...")
            transcript = self.recognizer.recognize_google(audio)
            logger.info(f"Transcription successful: {transcript}")
            return transcript
        except sr.UnknownValueError:
            logger.error("Google Speech Recognition could not understand the audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service; {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in transcribe_audio: {e}")
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