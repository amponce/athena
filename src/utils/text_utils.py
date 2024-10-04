import re

def clean_text_for_tts(text):
    # Remove asterisks and other unwanted punctuation
    cleaned_text = re.sub(r'[^\w\s]', '', text)
    # Optionally, remove other punctuation if needed
    # cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
    return cleaned_text