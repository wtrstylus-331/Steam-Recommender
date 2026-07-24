import os
from dotenv import load_dotenv

class OpenAIInstance:
    _instance = None
    api_key: str = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OpenAIInstance, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.refresh()
        if self._initialized:
            return

        self._initialized = True

    def refresh(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            print("No OpenAI API key stored in .env file able to be assigned to attribute!")
