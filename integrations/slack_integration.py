import os
from slack_sdk import WebClient

# Initialize Slack client if token is available
slack_token = os.getenv("SLACK_BOT_TOKEN")
if slack_token:
    slack_client = WebClient(token=slack_token)
else:
    slack_client = None
    print("Warning: SLACK_BOT_TOKEN not set. Slack functionalities will be disabled.")

def read_slack_messages(channel_id):
    if slack_client is None:
        print("Slack client not initialized. Skipping message retrieval.")
        return []
    try:
        response = slack_client.conversations_history(channel=channel_id, limit=10)
        messages = response['messages']
        return messages
    except Exception as e:
        print(f"Error reading Slack messages: {e}")
        return []