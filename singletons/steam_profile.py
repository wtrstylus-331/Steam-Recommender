# main web instance for inputted profile to display game inventory, stats, etc.
from typing import Optional, Union

class SteamGame:
    # attributes
    app_id: int
    app_name: str
    app_capsule_hash: str
    playtime_forever: int # minutes
    playtime_2weeks: int # optional, minutes

    def __init__(self, app_id: int, app_name: str, app_capsule_hash: str, playtime_forever: int):
        self.app_id = app_id
        self.app_name = app_name
        self.app_capsule_hash = app_capsule_hash
        self.playtime_forever = playtime_forever
        self.playtime_2weeks = -1

    def set_playtime_2weeks(self, playtime: int) -> None:
        """Only used for games played 'recently' by users"""
        self.playtime_2weeks = playtime

    def played_recently(self) -> bool:
        return self.playtime_2weeks > 0

    def get_playtime_hrs(self) -> float:
        return float(f"{self.playtime_forever / 60}:.1f")

    def get_2weeks_playtime_hrs(self) -> float:
        return float(f"{self.playtime_2weeks / 60}:.1f")


class SteamProfileInstance:
    # private attributes
    _instance = None
    _initialized = False

    # attributes
    steam_profile_id: Optional[int]
    steam_profile_name: Optional[str]
    steam_avatar_url: str
    steam_games: list[SteamGame]
    steam_game_count: int

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SteamProfileInstance, cls).__new__(cls)
        return cls._instance

    def __init__(self, summary: dict=None):
        if self._initialized:
            return

        if summary:
            self.set_profile(summary)
        else:
            self.steam_profile_id = None
            self.steam_profile_name = None
            self.steam_avatar_url = ""
        self.steam_games = []
        self.steam_game_count = 0

        self._initialized = True

    def set_profile(self, response: dict) -> None:
        """Take in raw dictionary <response> from the ISteamUser.GetPlayerSummaries method call."""
        details: dict = ((response.get("response")).get("players"))[0]
        self.steam_profile_id = int(details["steamid"])
        self.steam_profile_name = details["personaname"]
        self.steam_avatar_url = details["avatarfull"]

    def set_games(self, response: dict) -> None:
        """Take in raw dictionary <response> from the SteamUser.GetOwnedGames method call."""
        self.steam_game_count = int((response.get("response")).get("game_count"))
        games: list[dict] = (response.get("response")).get("games")

        for entry in games:
            appid: int = int(entry.get("appid"))
            name: str = entry.get("name")
            playtime_forever: int = int(entry.get("playtime_forever"))
            playtime_2weeks: Union[int, None] = entry.get("playtime_2weeks", None)
            capsule_hash: str = entry.get("img_icon_url")

            g_instance = SteamGame(appid, name, capsule_hash, playtime_forever)
            if playtime_2weeks:
                g_instance.set_playtime_2weeks(int(playtime_2weeks))

            self._add_game(g_instance)

    def get_games(self) -> list[SteamGame]:
        return self.steam_games

    def reset_games(self) -> None:
        self.steam_games = []

    def sort_games_by_appid(self) -> None:
        self.steam_games.sort(key=lambda x: x.app_id, reverse=False)

    def sort_games_by_name(self) -> None:
        self.steam_games.sort(key=lambda x: x.app_name, reverse=False)

    def sort_games_by_playtime(self, descending: bool=False) -> None:
        self.steam_games.sort(key=lambda x: x.playtime_forever, reverse=descending)

    def _add_game(self, game: SteamGame) -> None:
        self.steam_games.append(game)
        self.steam_games.sort(key=lambda x: x.app_name, reverse=False)
