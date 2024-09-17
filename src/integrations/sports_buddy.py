import os
import base64
from openai import OpenAI
import pyautogui
import logging

class SportsBuddy:
    def __init__(self, config):
        self.config = config
        self.client = self.create_openai_client()
        self.frame_path = os.path.join(os.getcwd(), "frames", "frame.jpg")
        self.is_active = False

    def create_openai_client(self):
        return OpenAI(api_key=self.config.OPENAI_API_KEY)

    def start(self):
        self.is_active = True
        return "Sports Buddy is now active and monitoring the screen."

    def stop(self):
        self.is_active = False
        return "Sports Buddy has stopped monitoring the screen."

    def status(self):
        return "Sports Buddy is active and ready to analyze frames." if self.is_active else "Sports Buddy is not active."

    def take_screenshot(self):
        try:
            os.makedirs(os.path.dirname(self.frame_path), exist_ok=True)
            screenshot = pyautogui.screenshot()
            screenshot.save(self.frame_path)
            logging.info(f"Screenshot saved to {self.frame_path}")
            return self.frame_path
        except Exception as e:
            logging.error(f"Error taking screenshot: {e}")
            return None

    def analyze_frame(self, user_prompt):
        if not self.is_active:
            return "Sports Buddy is not active. Please start it first."

        screenshot_path = self.take_screenshot()
        if not screenshot_path or not os.path.exists(screenshot_path):
            return "Failed to capture screenshot."
        
        try:
            base64_image = self.encode_image(screenshot_path)
            response = self.client.chat_completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sports analyst. Analyze the image for sports content. If there's no sports content, say so clearly. If there is, describe the game, score, and key events."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        ],
                    },
                ],
                max_tokens=500,
            )
            analysis = response.choices[0].message.content
            logging.info(f"Frame analysis: {analysis}")
            return analysis
        except Exception as e:
            logging.error(f"Error analyzing frame: {e}")
            return f"An error occurred while analyzing the frame: {str(e)}"

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')