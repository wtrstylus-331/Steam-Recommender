import os
from openai import OpenAI
from dotenv import load_dotenv

class OpenAIInstance:
    _instance: "OpenAIInstance" = None

    def __new__(cls) -> "OpenAIInstance":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            print("No OpenAI API key found!")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    def refresh(self) -> None:
        load_dotenv()
        new = os.getenv("OPENAI_API_KEY")

        if new != self.api_key:
            self.api_key = new
            self.client = OpenAI(api_key=self.api_key)

    def send_message(self, message):
        if not self.client:
            return None
