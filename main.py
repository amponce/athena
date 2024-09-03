import speech_recognition as sr
from openai import OpenAI
import os
import time
import tempfile
from pydub import AudioSegment
from pydub.playback import play
import io

# Initialize OpenAI client
OpenAI.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI()

# Create audio directory if it doesn't exist
os.makedirs("audio", exist_ok=True)

def analyze_audio(full_analysis, user_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a friendly and supportive assistant. 
                    You engage in natural, warm, and conversational interactions with the user.
                    Offer helpful responses, engage in casual conversation, and be encouraging. 
                    """,
                },
            ] + full_analysis + [{"role": "user", "content": user_prompt}],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in analyze_audio: {e}")
        return "I'm sorry, I encountered an error while processing your request."

def play_audio(text):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
        )

        # Load the audio data into an AudioSegment
        audio = AudioSegment.from_mp3(io.BytesIO(response.content))

        # Play the audio
        play(audio)
    except Exception as e:
        print(f"Error in play_audio: {e}")

def get_audio_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for speech...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            print("No speech detected within the timeout period.")
            return None

    return transcribe_audio(audio)

def transcribe_audio(audio):
    try:
        # Save audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio.get_wav_data())
            temp_audio_path = temp_audio.name

        # Transcribe the audio
        with open(temp_audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

        # Clean up the temporary file
        os.unlink(temp_audio_path)

        return transcript
    except Exception as e:
        print(f"Error in transcribe_audio: {e}")
        return None

def main():
    full_analysis = []
    while True:
        try:
            user_prompt = get_audio_input()
            if user_prompt is None:
                continue
            print("User:", user_prompt)
            analysis = analyze_audio(full_analysis, user_prompt)
            print("Assistant:", analysis)
            play_audio(analysis)
            time.sleep(1)  # Add a small delay after playing audio
            full_analysis.append({"role": "user", "content": user_prompt})
            full_analysis.append({"role": "assistant", "content": analysis})
        except KeyboardInterrupt:
            print("\nExiting the program.")
            break
        except Exception as e:
            print(f"An error occurred in main loop: {e}")

if __name__ == "__main__":
    main()