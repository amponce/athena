import sounddevice as sd
import numpy as np

duration = 5  # seconds
def audio_callback(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata) * 10
    print("|" * int(volume_norm))

with sd.InputStream(callback=audio_callback):
    sd.sleep(duration * 1000)
