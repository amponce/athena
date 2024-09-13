import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# User Configuration
USER_NAME = os.getenv("USER_NAME")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Speech Recognition Configuration
SPEECH_RECOGNITION_TIMEOUT = int(os.getenv("SPEECH_RECOGNITION_TIMEOUT"))
SPEECH_RECOGNITION_PHRASE_TIME_LIMIT = int(os.getenv("SPEECH_RECOGNITION_PHRASE_TIME_LIMIT"))

# Audio Playback Configuration
AUDIO_OUTPUT_DEVICE = os.getenv("AUDIO_OUTPUT_DEVICE", "default")

# Logging Configuration
DEBUG_LOGGING = os.getenv("DEBUG_LOGGING").upper() == "TRUE"

# Assistant Configuration
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
THREAD_ID = os.getenv("THREAD_ID")

# Athena Configuration
ATHENA_INSTRUCTIONS = f"""
You are Athena, a personal AI companion always ready to assist.
You are particularly good at drafting quick messages and responses in {USER_NAME}'s tone of voice.
Your primary user is named {USER_NAME}.
You interact naturally and warmly, engaging in meaningful conversations or performing tasks as requested.
You can manage Slack and GitHub activities, gather information from the internet, or simply chat.
When {USER_NAME} requests a task, acknowledge it and handle it promptly.
Maintain a friendly and supportive demeanor, ensuring interactions feel seamless and intuitive.
"""

ATHENA_TOOLS = [{"type": "code_interpreter"}, {"type": "file_search"}]
INTERPRETER_AUTO_RUN = os.getenv("INTERPRETER_AUTO_RUN").upper() == "TRUE"
OPENAI_MODEL = os.getenv("ATHENA_MODEL", "gpt-4o")
INTERPRETER_MODEL = os.getenv("ATHENA_MODEL", "gpt-4o")