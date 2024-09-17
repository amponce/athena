import threading
import queue
from ..assistant.openai_client import OpenAIClient
from ..assistant.thread_manager import ThreadManager
from ..search.tavily_client import TavilyClient
from ..audio.speech_recognition import SpeechRecognizer
from ..audio.text_to_speech import TextToSpeech
from ..integrations.sports_buddy import SportsBuddy
from ..utils.logger import logger
from ..config import Config
from datetime import datetime, timedelta

class Athena:
    def __init__(self, config: Config):
        self.config = config
        self.openai_client = OpenAIClient(config)
        self.thread_manager = ThreadManager(self.openai_client)
        self.tavily_client = TavilyClient(config)
        self.speech_recognizer = SpeechRecognizer(config)
        self.text_to_speech = TextToSpeech(config)
        self.last_date_refresh = datetime.now()
        self.interrupt_queue = queue.Queue()
        self.is_speaking = False
        self.is_dormant = False
        self.sports_buddy = SportsBuddy(config) if config.SPORTS_BUDDY_ENABLED else None

    def run(self):
        logger.info(f"Initializing Athena, {self.config.USER_NAME}'s personal AI companion...")
        logger.info(f"Using model: {self.config.OPENAI_MODEL}")
        self.openai_client.initialize_assistant()

        # Greeting
        greeting = f"Hello {self.config.USER_NAME}! Athena Here. What's on your mind?"
        logger.info(f"Athena: {greeting}")
        self.text_to_speech.play_audio(greeting)

        logger.info("Listening for speech...")
        while True:
            try:
                self.refresh_date_if_needed()
                user_prompt = self.speech_recognizer.get_audio_input()
                if user_prompt is None:
                    logger.info("Listening again...")
                    continue

                if self.is_dormant:
                    if "wake up" in user_prompt.lower():
                        self.is_dormant = False
                        wake_message = f"I'm awake, {self.config.USER_NAME}. How can I assist you?"
                        logger.info(f"Athena: {wake_message}")
                        self.text_to_speech.play_audio(wake_message)
                    continue

                if user_prompt.lower() in ["exit", "quit", "goodbye"]:
                    farewell = f"Goodbye, {self.config.USER_NAME}! Have a great day."
                    logger.info(f"Athena: {farewell}")
                    self.text_to_speech.play_audio(farewell)
                    break

                if user_prompt.lower() in ["standby", "sleep"]:
                    self.is_dormant = True
                    dormant_message = "Entering standby mode. Say 'wake up' when you need me again."
                    logger.info(f"Athena: {dormant_message}")
                    self.text_to_speech.play_audio(dormant_message)
                    continue

                logger.info(f"{self.config.USER_NAME}: {user_prompt}")
                
                if self.is_speaking:
                    self.interrupt_queue.put(user_prompt)
                    continue

                if "sports buddy" in user_prompt.lower():
                    response = self.handle_sports_buddy(user_prompt)
                else:
                    response = self.analyze_audio(user_prompt)
                self.speak_response(response)
            
            except KeyboardInterrupt:
                logger.info(f"\nThank you for chatting with Athena. Goodbye, {self.config.USER_NAME}!")
                break
            except Exception as e:
                logger.error(f"An error occurred: {e}. Athena is ready to assist with something else.")
            
            logger.info("Listening for speech...")

    def handle_sports_buddy(self, user_prompt):
        if not self.sports_buddy:
            return "Sports Buddy is not enabled."
        
        if "start" in user_prompt.lower():
            return self.sports_buddy.start()
        elif "stop" in user_prompt.lower():
            return self.sports_buddy.stop()
        elif "status" in user_prompt.lower():
            return self.sports_buddy.status()
        elif "check frame" in user_prompt.lower():
            analysis = self.sports_buddy.analyze_frame("What's happening in the game right now?")
            return f"Here's what I see in the latest frame: {analysis}"
        else:
            return "I didn't understand that Sports Buddy command. You can say 'start', 'stop', 'status', or 'check frame'."

    def speak_response(self, response):
        def speak_thread():
            self.is_speaking = True
            logger.info(f"Athena: {response}")
            self.text_to_speech.play_audio(response)
            self.is_speaking = False

        speak_thread = threading.Thread(target=speak_thread)
        speak_thread.start()

        while speak_thread.is_alive():
            try:
                interrupt = self.interrupt_queue.get(timeout=0.1)
                if interrupt:
                    self.text_to_speech.stop_audio()
                    logger.info(f"Interrupted: {interrupt}")
                    speak_thread.join()
                    return interrupt
            except queue.Empty:
                pass

        speak_thread.join()
        return None

    def refresh_date_if_needed(self):
        current_time = datetime.now()
        if current_time - self.last_date_refresh > timedelta(hours=1):
            self.openai_client.initialize_assistant()
            self.last_date_refresh = current_time
            logger.info("Refreshed assistant with current date.")

    def analyze_audio(self, user_prompt):
        thread_id = self.thread_manager.get_or_create_thread()
        if not thread_id:
            return "Failed to create or retrieve a thread. Cannot process the request."

        self.openai_client.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_prompt
        )

        run = self.openai_client.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.openai_client.assistant_id
        )

        while True:
            run = self.openai_client.wait_for_run_completion(thread_id, run.id)
            if run.status == 'requires_action':
                tool_outputs = self.openai_client.submit_tool_outputs(
                    thread_id, 
                    run.id, 
                    run.required_action.submit_tool_outputs.tool_calls,
                    self.tavily_client.search
                )
                run = self.openai_client.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            elif run.status == 'completed':
                break
            elif run.status == 'failed':
                return f"Run failed: {run.last_error}"

        messages = self.openai_client.client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=1
        )

        if messages.data:
            latest_message = messages.data[0]
            if latest_message.role == "assistant":
                response = latest_message.content[0].text.value
                return response
        
        return f"Hey {self.config.USER_NAME}, I didn't quite catch that. Mind rephrasing?"