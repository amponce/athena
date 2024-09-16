from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
import io
from ..utils.logger import logger
from ..config import Config

class TextToSpeech:
    def __init__(self, config: Config):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.config = config

    def play_audio(self, text, voice="nova"):
        try:
            if not isinstance(text, str):
                text = str(text)

            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
            )

            audio = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
            play(audio)
        except Exception as e:
            logger.error(f"Error in play_audio: {e}")

    def stop_audio(self):
        # This method is intentionally left empty as we're not using pygame anymore
        pass