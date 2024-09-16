import pytest
from unittest.mock import Mock, patch, call
from datetime import datetime, timedelta
from src.assistant.athena import Athena
from src.config import Config
import time
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module="speech_recognition")

@pytest.fixture
def mock_config():
    return Mock(spec=Config, USER_NAME="TestUser", OPENAI_MODEL="gpt-3.5-turbo")

@pytest.fixture
def athena(mock_config):
    with patch('src.assistant.athena.OpenAIClient'), \
         patch('src.assistant.athena.ThreadManager'), \
         patch('src.assistant.athena.TavilyClient'), \
         patch('src.assistant.athena.SpeechRecognizer'), \
         patch('src.assistant.athena.TextToSpeech'):
        yield Athena(mock_config)

def test_athena_initialization(athena, mock_config):
    assert athena.config == mock_config
    assert athena.is_speaking == False
    assert athena.is_dormant == False


@patch('src.assistant.athena.logger')
def test_run_greeting(mock_logger, athena, mock_config):
    athena.text_to_speech.play_audio = Mock()
    athena.speech_recognizer.get_audio_input = Mock(side_effect=["exit"])
    
    
    athena.run()
    
    expected_greeting = f"Hello {mock_config.USER_NAME}! I'm Athena, your AI assistant. How can I help you today?"
    expected_farewell = f"Goodbye, {mock_config.USER_NAME}! Have a great day."
    
    mock_logger.info.assert_any_call(f"Athena: {expected_greeting}")
    mock_logger.info.assert_any_call(f"Athena: {expected_farewell}")
    athena.text_to_speech.play_audio.assert_has_calls([
        call(expected_greeting),
        call(expected_farewell)
    ], any_order=False)

def test_speak_response(athena):
    test_response = "This is a test response."
    athena.text_to_speech.play_audio = Mock()
    
    result = athena.speak_response(test_response)
    
    assert result is None
    athena.text_to_speech.play_audio.assert_called_with(test_response)

def test_speak_response_with_interrupt(athena):
    test_response = "This is a test response."
    interrupt = "Interrupt message"
    
    def mock_play_audio(x):
        athena.interrupt_queue.put(interrupt)
        time.sleep(0.2)  # Simulate some processing time
    
    athena.text_to_speech.play_audio = Mock(side_effect=mock_play_audio)
    athena.text_to_speech.stop_audio = Mock()
    
    result = athena.speak_response(test_response)
    
    assert result == interrupt
    athena.text_to_speech.stop_audio.assert_called_once()

def test_refresh_date_if_needed(athena):
    athena.last_date_refresh = datetime.now() - timedelta(hours=2)
    athena.openai_client.initialize_assistant = Mock()
    
    athena.refresh_date_if_needed()
    
    athena.openai_client.initialize_assistant.assert_called_once()
    assert (datetime.now() - athena.last_date_refresh) < timedelta(minutes=1)

@patch('src.assistant.athena.logger')
def test_analyze_audio_success(mock_logger, athena):
    test_prompt = "What's the weather like?"
    test_response = "The weather is sunny today."
    
    athena.thread_manager.get_or_create_thread = Mock(return_value="test_thread_id")
    athena.openai_client.client.beta.threads.messages.create = Mock()
    athena.openai_client.client.beta.threads.runs.create = Mock()
    athena.openai_client.wait_for_run_completion = Mock(return_value=Mock(status='completed'))
    athena.openai_client.client.beta.threads.messages.list = Mock(return_value=Mock(
        data=[Mock(role="assistant", content=[Mock(text=Mock(value=test_response))])]
    ))
    
    result = athena.analyze_audio(test_prompt)
    
    assert result == test_response

@patch('src.assistant.athena.logger')
def test_analyze_audio_failure(mock_logger, athena, mock_config):
    test_prompt = "What's the weather like?"
    
    athena.thread_manager.get_or_create_thread = Mock(return_value=None)
    
    result = athena.analyze_audio(test_prompt)
    
    assert result == "Failed to create or retrieve a thread. Cannot process the request."

if __name__ == "__main__":
    pytest.main()