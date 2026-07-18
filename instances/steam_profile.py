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
    _stored_games: list[dict]

    # attributes
    steam_profile_id: Optional[int]
    steam_profile_name: Optional[str]
    steam_avatar_url: str
    current_steam_games: list[SteamGame]
    steam_games_map: dict[int, SteamGame]
    steam_game_count: int
    recent_game_count: int

    def __init__(self, summary: dict=None):
        if summary:
            self.set_profile(summary)
        else:
            self.steam_profile_id = None
            self.steam_profile_name = None
            self.steam_avatar_url = ""
        self.current_steam_games = []
        self._stored_games = []
        self.steam_games_map = {}
        self.steam_game_count = 0
        self.recent_game_count = 0

    def set_profile(self, response: dict) -> None:
        """Take in raw dictionary <response> from the ISteamUser.GetPlayerSummaries method call."""
        details: dict = ((response.get("response")).get("players"))[0]
        self.steam_profile_id = int(details["steamid"])
        self.steam_profile_name = details["personaname"]
        self.steam_avatar_url = details["avatarfull"]

    def set_games(self, response: dict) -> None:
        """Take in raw dictionary <response> from the SteamUser.GetOwnedGames method call."""
        print(response)
        if not response.get("response"):
            return

        try:
            self.steam_game_count = int((response.get("response")).get("game_count"))
            games: list[dict] = (response.get("response")).get("games")
            self._stored_games = games

            self._game_set_helper(len(games), games_list=games)

            counter = 0
            for game in self.current_steam_games:
                if game.played_recently():
                    counter += 1
            self.recent_game_count = counter
        # except TypeError as e:
        #     pass
        except Exception as e:
            return

        # match self.steam_game_count:
        #     case 0:
        #         self._stored_games = []
        #         self.current_steam_games = []
        #     case n if 1 <= n <= 100:
        #         self._game_set_helper(n, games)
        #     case n if 101 <= n:
        #         self._game_set_helper(75, games)

    def _game_set_helper(self, amount: int, games_list: list[dict]) -> None:
        for i in range(amount):
            appid: int = int(games_list[i].get("appid"))
            name: str = games_list[i].get("name")
            playtime_forever: int = int(games_list[i].get("playtime_forever"))
            playtime_2weeks: Union[int, None] = games_list[i].get("playtime_2weeks", None)
            capsule_hash: str = games_list[i].get("img_icon_url")

            g_instance = SteamGame(appid, name, capsule_hash, playtime_forever)
            if playtime_2weeks:
                g_instance.set_playtime_2weeks(int(playtime_2weeks))

            self._add_game(g_instance)

    def get_games(self) -> list[SteamGame]:
        return self.current_steam_games

    def reset_games(self) -> None:
        self.current_steam_games = []
        self.steam_games_map = {}

    def sort_games_by_appid(self) -> None:
        self.current_steam_games.sort(key=lambda x: x.app_id, reverse=False)

    def sort_games_by_name(self) -> None:
        self.current_steam_games.sort(key=lambda x: x.app_name, reverse=False)

    def sort_games_by_playtime(self, descending: bool=False) -> None:
        self.current_steam_games.sort(key=lambda x: x.playtime_forever, reverse=descending)

    def _add_game(self, game: SteamGame) -> None:
        self.current_steam_games.append(game)
        self.steam_games_map[game.app_id] = game
