from openai import OpenAI
from ..utils.logger import logger
from ..config import Config
from datetime import datetime

class OpenAIClient:
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.assistant_id = None

    def initialize_assistant(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        instructions = f"{self.config.ATHENA_INSTRUCTIONS}\n\nToday's date is {current_date}. Always refer to this date when discussing current events or news."
        
        if self.config.ASSISTANT_ID:
            try:
                assistant = self.client.beta.assistants.retrieve(self.config.ASSISTANT_ID)
                logger.info(f"Updating existing assistant with ID: {assistant.id}")
                assistant = self.client.beta.assistants.update(
                    assistant_id=self.config.ASSISTANT_ID,
                    instructions=instructions,
                    model=self.config.OPENAI_MODEL,
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
                self.assistant_id = assistant.id
                return self.assistant_id
            except Exception as e:
                logger.error(f"Error updating assistant: {e}")
        
        try:
            assistant = self.client.beta.assistants.create(
                name="Athena",
                instructions=instructions,
                model=self.config.OPENAI_MODEL,
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
            logger.info(f"New assistant created with ID: {assistant.id}")
            self.assistant_id = assistant.id
            return self.assistant_id
        except Exception as e:
            logger.error(f"Error creating assistant: {e}")
            return None

    def wait_for_run_completion(self, thread_id, run_id):
        while True:
            run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            logger.info(f"Current run status: {run.status}")
            if run.status in ['completed', 'failed', 'requires_action']:
                return run

    def submit_tool_outputs(self, thread_id, run_id, tool_calls, tavily_search_func):
        tool_outputs = []
        for tool_call in tool_calls:
            if tool_call.function.name == "tavily_search":
                query = eval(tool_call.function.arguments)["query"]
                search_result = tavily_search_func(query)
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": search_result
                })
        return tool_outputs