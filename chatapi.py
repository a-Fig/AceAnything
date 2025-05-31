from google import genai
from typing import List
from dotenv import load_dotenv
import os

from google.genai.types import Content
from google.genai import errors as genai_errors   # <-- important
import time
print("chatapi.py")


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_CLIENT_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# gemini-2.5-flash-preview-04-17
# gemini-2.0-flash
# gemini-2.0-flash-lite


class FlashChat:
    def __init__(self, directions: str = "You are a helpful assistant.", model: str = "gemini-2.0-flash"):
        self.chat = client.chats.create(model=model)
        self.directions = directions
        self.setup: bool = False

    def prompt(self, message: str = "") -> str:
        if not self.setup:
            self.chat.send_message(self.directions)
            self.setup = True
        return self.safe_prompt(message)

    def safe_prompt(self, message: str, max_tries: int = 5, base_backoff: float = 10.0):
        """
        Send a prompt to Gemini, retrying on 503 UNAVAILABLE.

        chat       – your google.genai Chat object
        message    – user / system message string
        max_tries  – total attempts before giving up
        base_backoff – seconds; real wait = base_backoff * 2**attempt
        """
        print(f"FlashChat.safe_prompt called with message: {message[:100]}... (length: {len(message)})")

        for attempt in range(max_tries):
            print(f"Attempt {attempt + 1}/{max_tries} to send message to Gemini")
            try:
                print("Calling Gemini API...")
                response = self.chat.send_message(message)
                print(f"Gemini API response received, text length: {len(response.text)}")
                print(f"Response text (first 100 chars): {response.text[:100]}...")
                return response.text
            except Exception as e:
                print(f"Exception caught in safe_prompt: {type(e).__name__}: {str(e)}")
                wait = base_backoff * (2 ** attempt)  # exponential backoff
                if attempt == max_tries - 1:
                    print(f"Max retries reached, raising exception: {e}")
                    raise

                print(f"Gemini error. retry {attempt + 1}/{max_tries} in {wait}s…")
                time.sleep(wait)

        print("All attempts failed, returning empty string")
        return ""

    def chat_history(self, user_label: str = "user> ", model_label: str = "model> ", user_end_label: str = "", model_end_label: str = "") -> str:
        history: str = ""
        for item in self.chat.get_history():
            message_label = user_label if item.role == 'user' else model_label
            end_label = user_end_label if item.role == 'user' else model_end_label

            for part in item.parts:
                history = f"{history}{message_label}{part.text}{end_label}"
                if history[-1] != '\n':
                    history = f"{history}\n"
        return history

    def raw_history(self) -> list[Content]:
        return self.chat.get_history()



def open_chat_with(fchat: FlashChat):
    user_message = input("user: ")
    while user_message != "stop":
        response = fchat.prompt(user_message)
        print(f"flash: {response}")
        user_message = input("user: ")
    return fchat.chat_history(user_label="User:\n   ", model_label="Gemini:\n   ")


if __name__ == '__main__':
    shorten_names = FlashChat("bot1")
    say_thankyou = FlashChat("bot2")
    print(open_chat_with(shorten_names))
    print(open_chat_with(say_thankyou))
