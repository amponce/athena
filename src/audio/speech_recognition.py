import speech_recognition as sr
from ..utils.logger import logger
from ..config import Config
import time

class SpeechRecognizer:
    def __init__(self, config: Config):
        self.recognizer = sr.Recognizer()
        self.config = config

    def get_audio_input(self):
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

        try:
            transcript = self.transcribe_audio(audio)
            if transcript:
                logger.info(f"Transcribed audio: {transcript}")
                return transcript
            else:
                logger.info("Transcription failed. Please try speaking again.")
                return None
        except sr.UnknownValueError:
            logger.info("Speech recognition could not understand the audio. Please try again.")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from speech recognition service; {e}")
            return None

    def transcribe_audio(self, audio):
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