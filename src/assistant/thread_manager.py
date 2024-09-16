from ..utils.logger import logger

class ThreadManager:
    def __init__(self, openai_client):
        self.openai_client = openai_client
        self.thread_id = None

    def get_or_create_thread(self):
        if self.thread_id:
            try:
                self.openai_client.client.beta.threads.retrieve(self.thread_id)
                return self.thread_id
            except Exception as e:
                logger.error(f"Error retrieving thread: {e}")
        
        try:
            thread = self.openai_client.client.beta.threads.create()
            self.thread_id = thread.id
            logger.info(f"New thread created with ID: {self.thread_id}")
            return self.thread_id
        except Exception as e:
            logger.error(f"Error creating thread: {e}")
            return None