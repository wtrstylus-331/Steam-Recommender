from django.apps import AppConfig
from instances.steam_web_api import SteamWebInstance
from instances.openai_instance import OpenAIInstance


class IndexConfig(AppConfig):
    name = "index"

    def ready(self):
        OpenAIInstance()
        SteamWebInstance()
