from django.apps import AppConfig
from singletons.steam_web_api import SteamWebInstance
from singletons.openai_instance import OpenAIInstance
from singletons.steam_profile import SteamProfileInstance


class IndexConfig(AppConfig):
    name = "index"

    def ready(self):
        OpenAIInstance.instance()
        SteamWebInstance.instance()
        SteamProfileInstance.instance()
