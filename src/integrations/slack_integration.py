import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.rtm_v2 import RTMClient
import time

class PersonalSlackMonitor:
    def __init__(self):
        self.slack_token = os.getenv("SLACK_USER_TOKEN")  # Use a user token instead of a bot token
        if self.slack_token:
            self.web_client = WebClient(token=self.slack_token)
            self.rtm_client = RTMClient(token=self.slack_token)
        else:
            print("Warning: SLACK_USER_TOKEN not set. Slack functionalities will be disabled.")
            self.web_client = None
            self.rtm_client = None
        
        self.monitored_channels = []
        self.user_id = self.get_user_id()

    def get_user_id(self):
        try:
            response = self.web_client.auth_test()
            return response["user_id"]
        except SlackApiError as e:
            print(f"Error getting user ID: {e}")
            return None

    def add_monitored_channel(self, channel_name):
        try:
            channel_id = self.get_channel_id(channel_name)
            if channel_id:
                self.monitored_channels.append(channel_id)
                print(f"Now monitoring channel: {channel_name}")
            else:
                print(f"Channel {channel_name} not found or you don't have access to it.")
        except SlackApiError as e:
            print(f"Error adding channel: {e}")

    def get_channel_id(self, channel_name):
        try:
            response = self.web_client.conversations_list(types="public_channel,private_channel")
            for channel in response["channels"]:
                if channel["name"] == channel_name:
                    return channel["id"]
            return None
        except SlackApiError as e:
            print(f"Error getting channel ID: {e}")
            return None

    def read_recent_messages(self, channel_id, limit=10):
        try:
            response = self.web_client.conversations_history(channel=channel_id, limit=limit)
            return response['messages']
        except SlackApiError as e:
            print(f"Error reading messages: {e}")
            return []

    def start_rtm(self):
        @self.rtm_client.on("message")
        def handle_message(client: RTMClient, event: dict):
            if event['channel'] in self.monitored_channels:
                print(f"New message in monitored channel: {event['text']}")
                # Here you can add logic to process the message with your AI assistant
                # For example: self.process_message(event['text'])

    def run(self):
        if not self.web_client or not self.rtm_client:
            print("Slack client not initialized. Cannot run Slack integration.")
            return

        print("Starting personal Slack monitor...")
        try:
            self.start_rtm()
            self.rtm_client.start()
        except SlackApiError as e:
            print(f"Error starting RTM client: {e}")

    def process_message(self, message):
        # This is where you'd integrate with your AI assistant
        # For example:
        response = self.ai_assistant.analyze(message)
        self.handle_ai_response(response)
        pass

# Usage example
if __name__ == "__main__":
    slack_monitor = PersonalSlackMonitor()
    slack_monitor.add_monitored_channel("debt-devs-internal")
    slack_monitor.add_monitored_channel("team-engineering")
    slack_monitor.run()