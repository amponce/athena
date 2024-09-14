import os
import io
import json
import time
import re
import tempfile
from openai import OpenAI
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
from tavily import TavilyClient
from config import *
from integrations.interpreter_integration import start_interpreter_session
from functools import lru_cache
from datetime import datetime

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
assistant_id = None
thread_id = None

# Initialize Tavily client
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def get_search_date_range():
    now = datetime.now()
    current_month = now.strftime("%B")
    current_year = now.year
    next_year = current_year + 1
    return f"({current_month} OR September) ({current_year} OR {next_year})"

@lru_cache(maxsize=100)
@lru_cache(maxsize=100)
def tavily_search(query):
    date_range = get_search_date_range()
    updated_query = f"{query} {date_range}"
    print(f"Performing Tavily search for query: {updated_query}")
    try:
        search_result = tavily_client.get_search_context(updated_query, search_depth="advanced", max_tokens=8000)
        print(f"Tavily search result type: {type(search_result)}")
        print(f"Tavily search result: {search_result[:500]}...")  # Print first 500 characters of the result
        
        if isinstance(search_result, str):
            search_result = json.loads(search_result)
        
        summary = summarize_search_results(search_result, query)  # Pass the original query here
        return json.dumps({"summary": summary, "full_results": search_result})
    except Exception as e:
        print(f"Error in Tavily search: {e}")
        return json.dumps({"error": str(e)})

def summarize_search_results(search_results, query):
    if not isinstance(search_results, list):
        return "Sorry, I couldn't find any relevant information."
    
    current_year = datetime.now().year
    next_year = current_year + 1
    
    relevant_results = []
    for result in search_results:
        content = result.get('content', '')
        url = result.get('url', '')
        
        # Check if the content mentions the current or next year
        if str(current_year) in content or str(next_year) in content:
            relevant_results.append((content, url))
    
    if not relevant_results:
        return f"I couldn't find any horror movies specifically for September {current_year} or {next_year}. Would you like me to search for horror movies in general?"
    
    summary = f"Here are some exciting horror movies coming up:\n\n"
    for content, url in relevant_results[:3]:  # Limit to top 3 results for brevity
        # Extract a relevant sentence or two
        sentences = re.split(r'(?<=[.!?])\s+', content)
        relevant_text = ' '.join(sentences[:2])  # Take first two sentences
        
        summary += f"• {relevant_text}\n"
    
    summary += f"\nThese are just a few of the upcoming releases. Would you like more details on any of these movies?"
    
    return summary
    
def get_or_create_thread():
    global thread_id
    if thread_id:
        try:
            client.beta.threads.retrieve(thread_id)
            return thread_id
        except Exception as e:
            print(f"Error retrieving thread: {e}")
    
    try:
        thread = client.beta.threads.create()
        thread_id = thread.id
        print(f"New thread created with ID: {thread_id}")
        return thread_id
    except Exception as e:
        print(f"Error creating thread: {e}")
        return None

def initialize_assistant():
    global assistant_id
    if ASSISTANT_ID:
        try:
            assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
            print(f"Updating existing assistant with ID: {assistant.id}")
            assistant = client.beta.assistants.update(
                assistant_id=ASSISTANT_ID,
                instructions=ATHENA_INSTRUCTIONS,
                model=OPENAI_MODEL,
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "tavily_search",
                        "description": "Search the web for recent and relevant information.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "The search query to use."},
                            },
                            "required": ["query"]
                        }
                    }
                }]
            )
            assistant_id = assistant.id
            return assistant_id
        except Exception as e:
            print(f"Error updating assistant: {e}")
    
    # If no existing assistant, create a new one
    try:
        assistant = client.beta.assistants.create(
            name="Athena",
            instructions=ATHENA_INSTRUCTIONS,
            model=OPENAI_MODEL,
            tools=[{
                "type": "function",
                "function": {
                    "name": "tavily_search",
                    "description": "Search the web for recent and relevant information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query to use."},
                        },
                        "required": ["query"]
                    }
                }
            }]
        )
        print(f"New assistant created with ID: {assistant.id}")
        assistant_id = assistant.id
        return assistant_id
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return None

def wait_for_run_completion(thread_id, run_id):
    while True:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print(f"Current run status: {run.status}")
        if run.status == 'requires_action':
            print(f"Run requires action: {run.required_action}")
        if run.status in ['completed', 'failed', 'requires_action']:
            return run

def submit_tool_outputs(thread_id, run_id, tool_calls):
    tool_outputs = []
    for tool_call in tool_calls:
        if tool_call.function.name == "tavily_search":
            query = json.loads(tool_call.function.arguments)["query"]
            search_result = tavily_search(query)
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": search_result
            })
    return tool_outputs

@lru_cache(maxsize=100)
def analyze_audio(user_prompt):
    if not client.api_key or not assistant_id:
        return "OpenAI functionalities are disabled or assistant is not initialized. Cannot analyze audio."

    try:
        thread_id = get_or_create_thread()
        if not thread_id:
            return "Failed to create or retrieve a thread. Cannot process the request."

        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        while True:
            run = wait_for_run_completion(thread_id, run.id)
            if run.status == 'requires_action':
                tool_outputs = submit_tool_outputs(thread_id, run.id, run.required_action.submit_tool_outputs.tool_calls)
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            elif run.status == 'completed':
                break
            elif run.status == 'failed':
                return f"Run failed: {run.last_error}"

        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=1
        )

        if messages.data:
            latest_message = messages.data[0]
            if latest_message.role == "assistant":
                return latest_message.content[0].text.value
        
        return f"I'm sorry, {USER_NAME}, I didn't receive a response. How else can I assist you?"

    except Exception as e:
        print(f"Error in analyze_audio: {e}")
        return f"I'm sorry, {USER_NAME}, I encountered an error while processing your request. How can I help you differently?"

def play_audio(text, voice="nova"):
    try:
        if client is None:
            print("OpenAI client not initialized. Skipping text-to-speech.")
            return
        if not isinstance(text, str):
            text = str(text)

        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
        )

        audio = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
        play(audio)
    except Exception as e:
        print(f"Error in play_audio: {e}")

def get_audio_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for speech...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=SPEECH_RECOGNITION_TIMEOUT, phrase_time_limit=SPEECH_RECOGNITION_PHRASE_TIME_LIMIT)
            print("Audio captured, processing...")
        except sr.WaitTimeoutError:
            print("No speech detected within the timeout period.")
            return None

    try:
        transcript = transcribe_audio(audio)
        if transcript:
            print(f"Transcribed audio: {transcript}")
            return transcript
        else:
            print("Transcription failed. Please try speaking again.")
            return None
    except sr.UnknownValueError:
        print("Speech recognition could not understand the audio. Please try again.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from speech recognition service; {e}")
        return None

@lru_cache(maxsize=100)
def transcribe_audio(audio):
    if client is None:
        print("OpenAI client not initialized. Skipping transcription.")
        return None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio.get_wav_data())
            temp_audio_path = temp_audio.name

        with open(temp_audio_path, "rb") as audio_file:
            start_time = time.time()
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            ).strip()
            print(f"Time to transcribe audio: {time.time() - start_time:.2f} seconds")

        os.unlink(temp_audio_path)
        return transcript if transcript else None
    except Exception as e:
        print(f"Error in transcribe_audio: {e}")
        return None

def main():
    global assistant_id
    print(f"Initializing Athena, {USER_NAME}'s personal AI companion...")
    print(f"Using model: {OPENAI_MODEL}")
    assistant_id = initialize_assistant()
    if not assistant_id:
        print("Failed to initialize assistant. Exiting.")
        return

    print("Listening for speech...")
    while True:
        try:
            user_prompt = get_audio_input()
            if user_prompt is None:
                print("Listening again...")
                continue
            if user_prompt.lower() in ["exit", "quit", "goodbye"]:
                print(f"Athena: Goodbye, {USER_NAME}! Have a great day.")
                break
            
            print(f"{USER_NAME}:", user_prompt)
            
            if user_prompt.lower() == "start open interpreter":
                response = start_interpreter_session(get_audio_input, play_audio)
                print("Athena:", response)
                play_audio(response)
            else:
                analysis = analyze_audio(user_prompt)
                print("Athena:", analysis)
                play_audio(analysis)
            
            time.sleep(1)  # Small delay after playing audio
        except KeyboardInterrupt:
            print(f"\nThank you for chatting with Athena. Goodbye, {USER_NAME}!")
            break
        except Exception as e:
            print(f"An error occurred: {e}. Athena is ready to assist with something else.")
        
        print("Listening for speech...")

if __name__ == "__main__":
    main()