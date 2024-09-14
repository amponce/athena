import interpreter
from config import OPENAI_API_KEY, OPENAI_MODEL, INTERPRETER_AUTO_RUN

def initialize_interpreter():
    interpreter.api_key = OPENAI_API_KEY
    interpreter.model = OPENAI_MODEL
    interpreter.auto_run = INTERPRETER_AUTO_RUN

def run_interpreter_task(task):
    try:
        interpreter.reset()  # Reset the interpreter before each task
        response = interpreter.chat(task)
        return f"Task completed. {response}"
    except Exception as e:
        return f"Error executing task: {str(e)}"

def start_interpreter_session(get_audio_input, play_audio):
    print("Starting Open Interpreter session. Say 'Exit Interpreter' to end the session.")
    initialize_interpreter()
    
    while True:
        user_input = get_audio_input()
        if user_input is None:
            continue
        if user_input.lower() == "exit interpreter":
            return "Open Interpreter session ended."
        
        try:
            response = run_interpreter_task(user_input)
            print("Open Interpreter:", response)
            play_audio(response, voice="onyx")  # Using a different voice for Open Interpreter
        except Exception as e:
            error_message = f"Error in Open Interpreter: {str(e)}"
            print(error_message)
            play_audio(error_message, voice="onyx")