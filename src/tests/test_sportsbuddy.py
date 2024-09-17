import pytest
from unittest.mock import Mock, patch
from src.integrations.sports_buddy import SportsBuddy

@pytest.fixture
def sports_buddy():
    config = Mock()
    config.OPENAI_API_KEY = "test_key"
    return SportsBuddy(config)

@patch.object(SportsBuddy, 'create_openai_client')
def test_analyze_frame(mock_create_client, sports_buddy):
    sports_buddy.is_active = True  # Ensure Sports Buddy is active
    sports_buddy.take_screenshot = Mock(return_value=sports_buddy.frame_path)
    sports_buddy.encode_image = Mock(return_value="base64_encoded_image")

    # Create a mock for the OpenAI client
    mock_client = Mock()
    mock_create_client.return_value = mock_client

    # Mock the chat.completions.create method
    mock_completion = Mock()
    mock_completion.choices = [Mock(message=Mock(content="Test analysis"))]
    mock_client.chat_completions.create.return_value = mock_completion

    analysis = sports_buddy.analyze_frame("What's the score?")
    assert analysis == "Test analysis"

    # Verify that the OpenAI client was called with the correct arguments
    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a sports analyst. Analyze the image for sports content. If there's no sports content, say so clearly. If there is, describe the game, score, and key events."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's the score?"},
                    {
                        "type": "image_url",
                        "image_url": "data:image/jpeg;base64,base64_encoded_image",
                    },
                ],
            },
        ],
        max_tokens=500,
    )