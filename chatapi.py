from google import genai
from typing import List
from dotenv import load_dotenv
import os

from google.genai.types import Content

print("chatapi.py")


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_CLIENT_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# gemini-2.5-flash-preview-04-17
# gemini-2.0-flash
# gemini-2.0-flash-lite


class FlashChat:
    def __init__(self, directions: str = "", model: str = "gemini-2.0-flash"):
        self.chat = client.chats.create(model=model)
        if directions != "":
            self.chat.send_message(directions)

    def prompt(self, message: str = "") -> str:
        return self.chat.send_message(message).text

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


shorten_names = FlashChat("bot1")
say_thankyou = FlashChat("bot2")


def open_chat_with(fchat: FlashChat):
    user_message = input("user: ")
    while user_message != "stop":
        response = fchat.prompt(user_message)
        print(f"flash: {response}")
        user_message = input("user: ")
    return fchat.chat_history(user_label="Tyler:\n   ", model_label="Gemini:\n   ")


if __name__ == '__main__':
   print(open_chat_with(say_thankyou))