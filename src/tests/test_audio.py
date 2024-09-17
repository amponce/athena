import sounddevice as sd
import numpy as np
import pytest
import queue

# Duration for which we will capture audio
duration = 5  # seconds

# This will store audio data for verification in the test
audio_data_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    # Put the audio data into a queue for testing
    audio_data_queue.put(indata)

    # For logging purposes (simulating a visual volume indicator)
    volume_norm = np.linalg.norm(indata) * 10
    print("|" * int(volume_norm))

@pytest.fixture
def audio_test_setup():
    """Set up the test by creating an input stream and providing the callback."""
    # Create the input stream with the callback
    with sd.InputStream(callback=audio_callback):
        sd.sleep(duration * 1000)  # Let the input stream capture audio for 'duration' seconds

@pytest.mark.timeout(10)  # Set a timeout to ensure the test doesn't run indefinitely
def test_audio_capture(audio_test_setup):
    """Test that audio data is being captured and processed correctly."""
    # Wait for audio data to accumulate
    audio_frames = []
    while not audio_data_queue.empty():
        audio_frames.append(audio_data_queue.get())

    # Ensure that some audio data was captured
    assert len(audio_frames) > 0, "No audio data captured during the test."
    
    # Further check that the captured audio frames contain valid data
    for frame in audio_frames:
        assert frame.size > 0, "Empty audio frame captured."
        assert np.any(frame), "Captured audio frame contains all zeros, indicating no signal."

    print("Audio capture and callback execution passed!")

if __name__ == "__main__":
    pytest.main([__file__])
