# Open AI Whisper TTS Assistant

## Overview
TTS Assistant is an interactive AI system that combines speech recognition, natural language processing, and text-to-speech capabilities. It allows users to have spoken conversations with an AI assistant powered by OpenAI's GPT models.

## Features
- Speech recognition for user input
- Natural language processing using OpenAI's GPT models
- Text-to-speech output for AI responses
- Continuous conversation flow

## Requirements
- Python 3.x
- OpenAI API key (set as an environment variable `OPENAI_API_KEY`)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/amponce/tts_assistant.git
   cd tts_assistant
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

**Note:** If you encounter issues with PyAudio, use Homebrew to install PortAudio. On macOS, you can install PortAudio by opening your terminal and running the following command:
```
brew install portaudio
```

3. Set up your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

Run the main script:
- The assistant will prompt you to speak.
- Begin speaking when prompted. You can speak for as long as you like.
- Say "done" or remain silent for 2 seconds to indicate you've finished speaking.
- The AI will process your input and respond verbally.
- This process continues until you interrupt the program.

## Files
- `main.py`: The main script that runs the TTS Assistant.
- `requirements.txt`: List of Python packages required for the project.

## Troubleshooting
- If you encounter issues with audio input or output, ensure your microphone and speakers are properly configured.
- For "Access Denied" errors, try running the script with administrator privileges.

## Contributing
Contributions to improve TTS Assistant are welcome. Please feel free to submit pull requests or open issues to discuss proposed changes or report bugs.

## License
[ MIT ]
