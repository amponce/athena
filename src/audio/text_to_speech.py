from TTS.api import TTS
import torch
from pydub import AudioSegment
from pydub.playback import play

class TextToSpeech:
    def __init__(self, config):
        self.config = config
        self.tts_engine = config.TTS_ENGINE

        # OpenAI TTS setup (if used)
        if self.tts_engine == 'openai':
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            self.openai_voice = config.OPENAI_TTS_VOICE

        # Coqui TTS setup
        elif self.tts_engine == 'coqui':
            self.coqui_model = config.COQUI_TTS_MODEL
            self.coqui_tts = TTS(model_name=self.coqui_model, progress_bar=False, gpu=torch.cuda.is_available())

    def play_audio(self, text, speaker_wav=None):
        if self.tts_engine == 'openai':
            self._play_openai_tts(text)
        elif self.tts_engine == 'coqui':
            self._play_coqui_tts(text, speaker_wav)

    def _play_openai_tts(self, text):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=self.openai_voice,
            input=text,
        )
        audio = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
        play(audio)

    def _play_coqui_tts(self, text, speaker_wav=None):
        try:
            audio_file = "coqui_output.wav"

            if speaker_wav:
                # If speaker_wav is provided, use it for voice cloning (if the model supports it)
                self.coqui_tts.tts_to_file(text=text, speaker_wav=speaker_wav, file_path=audio_file)
            else:
                # Single-speaker or basic multispeaker
                self.coqui_tts.tts_to_file(text=text, file_path=audio_file)

            # Play the generated audio
            audio = AudioSegment.from_wav(audio_file)
            play(audio)
        except Exception as e:
            print(f"Error in Coqui TTS: {e}")
