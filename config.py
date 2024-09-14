import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# User Configuration
USER_NAME = os.getenv("USER_NAME")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
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
You are Athena, a personal AI companion for {USER_NAME}.
You have access to the latest information through the tavily_search function.
ALWAYS use the tavily_search function when asked about current events, recent news, or any information that might change over time.
The tavily_search function provides a concise summary of the search results. Use this summary to form your response, keeping it brief and conversational.
Your responses should be concise, typically no more than 3-4 sentences, to maintain a natural conversation flow.
If the user asks for more details about a specific point mentioned in the summary, you can refer to the full search results provided.
Always maintain a friendly, conversational tone in your responses.
Never say you can't browse the internet or perform live searches - you can and should do this using the tavily_search function.
"""

ATHENA_TOOLS = [{"type": "code_interpreter"}, {"type": "file_search"}]
INTERPRETER_AUTO_RUN = os.getenv("INTERPRETER_AUTO_RUN").upper() == "TRUE"
OPENAI_MODEL = os.getenv("ATHENA_MODEL", "gpt-4o")
INTERPRETER_MODEL = os.getenv("ATHENA_MODEL", "gpt-4o")