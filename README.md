# Athena: Advanced AI Assistant

## Overview
Athena is an advanced AI assistant that combines speech recognition, natural language processing, and text-to-speech capabilities. It is designed to provide a seamless, conversational interface for accessing information and performing tasks across multiple platforms and services.

## Features
- Speech recognition for user input
- Natural language processing using OpenAI's GPT models
- Text-to-speech output for AI responses
- Web search capabilities using the Tavily API
- Continuous conversational flow

### Roadmap
- Integration with multiple APIs and services (e.g., Slack, GitHub, movie databases, Reddit, CoinMarketCap, Google APIs, email, calendars, etc.)

## Requirements
- Python 3.11+
- OpenAI API key
- Tavily API key
- Additional API keys as needed for extra integrations

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/amponce/athena.git
   cd athena
   ```
   (Optional) Create a virtual environment to isolate dependencies:

   On macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   On Windows:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file based on the `.env.example` in the root directory and add your API keys:

   ```
   OPENAI_API_KEY=OPENAI_API_KEY
   ASSISTANT_ID=ASSISTANT_ID
   # https://app.tavily.com/
   TAVILY_API_KEY=TAVILY_API_KEY
   USER_NAME=Aaron
   OPENAI_MODEL=gpt-4o
   SPEECH_RECOGNITION_TIMEOUT=15
   SPEECH_RECOGNITION_PHRASE_TIME_LIMIT=10
   DEBUG_LOGGING=true
   INTERPRETER_AUTO_RUN=false
   TTS_ENGINE=coqui # or openai 
   ## TTS 
   USE_WHISPER=false # or true will download the whisper model
   OPENAI_TTS_VOICE="nova"
   ## Coqui TTS
   COQUI_TTS_VOICE="p335"
   COQUI_TTS_MODEL="tts_models/en/vctk/vits"
   ```

**Note:** 

If you encounter issues with PyAudio, install PortAudio. On macOS, you can use Homebrew:
   ```bash
   brew install portaudio
   
   ```
If you are using freemodels like coqui, you may need to install additional dependencies:

```bash
brew install espeak-ng
```
Windows users can download the installer from here:

```
https://github.com/espeak-ng/espeak-ng/releases/download/1.51/espeak-ng-X64.msi

```

## Key Components

### Main Script (`main.py`)
The entry point of the application, handling the primary conversation loop and integrating all components.

### OpenAI Assistant Integration
Leverages OpenAI's GPT models for advanced language understanding and generation.

### Tavily Search Integration
Implements web search functionality using the Tavily API to provide up-to-date information from the web.

### Speech Recognition and Text-to-Speech
Enables voice input and output for a hands-free conversational experience.

## Configuration

The `config.py` file contains configuration settings, including API keys and model parameters. Ensure all required keys are correctly configured.

## Future Development
Future plans include integrating with additional APIs and services such as Slack, GitHub, movie databases, Reddit, CoinMarketCap, Google APIs, email, and calendar functionalities.

## Contributing
Contributions to improve Athena are welcome! Please feel free to submit pull requests or open issues to discuss proposed changes or report bugs.

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgements
- OpenAI for their GPT models and Assistant API
- Tavily for their search API

## Disclaimer
This project is for educational and personal use. Ensure compliance with the terms of service for all integrated APIs and services.

