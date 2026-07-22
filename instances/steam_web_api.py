import json
import os, requests, steamspypi
from typing import Union

from dotenv import load_dotenv
from steam.webapi import WebAPI

class SteamWebInstance:
    _instance = None
    _initialized: bool = False

    api_key: str
    web_api: WebAPI
    profile_summary: dict
    popular_tags: list[dict[str, list[str]]]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SteamWebInstance, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        load_dotenv()
        self.api_key = os.getenv("STEAM_WEB_API_KEY")

        if not self.api_key:
            raise AttributeError("No Steam Web API key stored in .env file able to be assigned to attribute!")

        self.web_api = WebAPI(key=self.api_key)
        self.profile_summary = {}
        self._initialized = True

    def id_from_vanity_url(self, vanity_id: str) -> int:
        res = dict(self.web_api.call('ISteamUser.ResolveVanityURL', vanityurl=vanity_id, url_type=1))
        return int((res.get('response')).get('steamid'))

    def get_summary_from_id(self, steamid: int) -> dict:
        summary = self.web_api.call('ISteamUser.GetPlayerSummaries', key=self.api_key, steamids=steamid)
        self.profile_summary = summary
        return summary

    def set_summary_from_id(self, steamid: int) -> None:
        summary = self.web_api.call('ISteamUser.GetPlayerSummaries', key=self.api_key, steamids=steamid)
        self.profile_summary = summary

    def get_user_owned_games(self, steamid: int,
                             show_app_info: bool = True,
                             include_freebies: bool = True,
                             app_ids_filter: int = 0,
                             include_free_sub: bool = False,
                             language: str = "en-us",
                             include_extra_appinfo: bool = True) -> dict:
        return self.web_api.call(
            'IPlayerService.GetOwnedGames',
            key=self.api_key,
            steamid=steamid,
            include_appinfo=show_app_info,
            include_played_free_games=include_freebies,
            appids_filter=app_ids_filter, #??? changing values from 0 to 5 mil don't seem to be doing anything for the return value
            include_free_sub=include_free_sub,
            language=language,
            include_extended_appinfo=include_extra_appinfo,
            skip_unvetted_apps=True # optional method parameter
        )

# def genres_from_appid(appid: int) -> Union[list[dict], None]:
#     response = requests.get(f'https://store.steampowered.com/api/appdetails?appids={appid}&l=en')
#     if response.status_code == 200:
#         return ((dict(response.json()).get(f'{appid}')).get('data')).get('genres')
#     return None

# more condensed approach
def misc_app_details(appid: int, tag_limit: int=5) -> Union[dict[str, list], None]:
    """Returns a dictionary of lists of genres and tags respectively from the provided <appid>."""
    result = {}

    data_request = {
        'request': 'appdetails',
        'appid': f'{appid}'
    }
    data: dict = steamspypi.download(data_request)

    genre_list: list[str] = [x.strip() for x in data.get('genre').split(',')]
    tags_dict: dict[str, int] = data.get('tags').copy()
    tag_list: list[str] = []
    counter = tag_limit
    while len(tags_dict) > 0 and counter > 0:
        max_ = max(tags_dict, key=tags_dict.get)
        tag_list.append(str(max_))
        tags_dict.pop(max_)
        counter -= 1

    result['genres'] = genre_list
    result['tags'] = tag_list

    return result
