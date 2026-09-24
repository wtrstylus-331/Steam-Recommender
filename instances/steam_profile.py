# main web instance for inputted profile to display game inventory, stats, etc.

class SteamGame:
    # attributes
    app_id: int
    app_name: str
    app_capsule_hash: str
    capsule_file_name: str
    playtime_forever: int # minutes
    playtime_forever_hrs: float
    playtime_2weeks: int | None # optional, minutes

    def __init__(
            self,
            app_id: int,
            app_name: str,
            app_capsule_hash: str,
            capsule_file_name: str,
            playtime_forever: int
    ):
        self.app_id = app_id
        self.app_name = app_name
        self.app_capsule_hash = app_capsule_hash
        self.capsule_file_name = capsule_file_name
        self.playtime_forever = playtime_forever
        self.playtime_forever_hrs = self.get_playtime_hrs()
        self.playtime_2weeks = -1

    def set_playtime_2weeks(self, playtime: int) -> None:
        """Only used for games played 'recently' by users"""
        self.playtime_2weeks = playtime

    def played_recently(self) -> bool:
        return self.playtime_2weeks > 0

    def get_playtime_hrs(self) -> float:
        hours = self.playtime_forever / 60
        return int(hours * 10) / 10

    def get_2weeks_playtime_hrs(self) -> float:
        hours = self.playtime_2weeks / 60
        return int(hours * 10) / 10


class SteamProfileInstance:
    _instance = None
    _stored_games: list[dict]
    _displayed_index: int

    # attributes
    steam_profile_id: int | None #Optional[int]
    steam_profile_name: str | None #Optional[str]
    steam_avatar_url: str
    current_steam_games: list[SteamGame]
    displayed_steam_games: list[SteamGame]
    displayed_recent_games: list[SteamGame]
    steam_games_map: dict[int, SteamGame]
    steam_game_count: int
    recent_game_count: int
    personaState: int | None  # 0 means offline, 1 means online/in-game
    playingGameId: int | None

    def __init__(self, summary: dict=None):
        if summary:
            self.set_profile(summary)
        else:
            self.steam_profile_id = None
            self.steam_profile_name = None
            self.steam_avatar_url = ""
        self.current_steam_games = []
        self.displayed_steam_games = []
        self.displayed_recent_games = []
        self._stored_games = []
        self.steam_games_map = {}
        self.steam_game_count = 0
        self.recent_game_count = 0
        self._displayed_index = 0
        self.personaState = None
        self.playingGameId = None

    def set_profile(self, response: dict) -> None:
        """Take in raw dictionary <response> from the ISteamUser.GetPlayerSummaries method call."""
        details: dict = ((response.get("response")).get("players"))[0]
        self.steam_profile_id = int(details["steamid"])
        self.steam_profile_name = details["personaname"]
        self.steam_avatar_url = details["avatarfull"]
        self.personaState = details.get("personastate")
        self.playingGameId = details.get("gameid")

    def set_games(self, response: dict) -> None:
        """Take in raw dictionary <response> from the SteamUser.GetOwnedGames method call."""
        print(response)
        if not response.get("response"): #profile is privated (?)
            self.steam_game_count = -1
            self.recent_game_count = -1
            return

        try:
            self.steam_game_count = int((response.get("response")).get("game_count"))
            games: list[dict] = (response.get("response")).get("games")
            self._stored_games = games

            self._game_set_helper(len(games), games_list=games)
            self.sort_games_by_name()

            self.displayed_steam_games = self.current_steam_games[self._displayed_index:self._displayed_index + 8]
            self._displayed_index += 8

            self.recent_game_count = sum([1 for g in self.current_steam_games if g.played_recently()])
        # except TypeError as e:
        #     pass
        except Exception as e:
            self.steam_game_count = -2
            self.recent_game_count = -2
            return

    def _game_set_helper(self, amount: int, games_list: list[dict]) -> None:
        for i in range(amount):
            appid: int = int(games_list[i].get("appid"))
            name: str = games_list[i].get("name")
            playtime_forever: int = int(games_list[i].get("playtime_forever"))
            playtime_2weeks: int | None = games_list[i].get("playtime_2weeks", None)
            capsule_hash: str = games_list[i].get("img_icon_url")
            capsule_file_name: str = games_list[i].get("capsule_filename")

            g_instance = SteamGame(appid, name, capsule_hash, capsule_file_name, playtime_forever)
            is_recent = False
            if playtime_2weeks:
                g_instance.set_playtime_2weeks(int(playtime_2weeks))
                is_recent = True

            self._add_game(g_instance, is_recent)

    def get_games(self) -> list[SteamGame]:
        return self.displayed_steam_games

    def get_to_lazyload(self) -> list[SteamGame]:
        out = self.current_steam_games[self._displayed_index : self._displayed_index + 8]
        self._displayed_index += 8
        return out

    def reset_games(self) -> None:
        self.current_steam_games = []
        self.steam_games_map = {}

    def sort_games_by_appid(self) -> None:
        self.current_steam_games.sort(key=lambda x: x.app_id, reverse=False)
        self.displayed_steam_games.sort(key=lambda x: x.app_id, reverse=False)

    def sort_games_by_name(self) -> None:
        self.current_steam_games.sort(key=lambda x: x.app_name, reverse=False)
        self.displayed_steam_games.sort(key=lambda x: x.app_name, reverse=False)

    def sort_games_by_playtime(self, descending: bool=False) -> None:
        self.current_steam_games.sort(key=lambda x: x.playtime_forever, reverse=descending)
        self.displayed_steam_games.sort(key=lambda x: x.playtime_forever, reverse=descending)

    def _add_game(self, game: SteamGame, is_recent: bool) -> None:
        if is_recent:
            self.displayed_recent_games.append(game)

        self.current_steam_games.append(game)
        self.steam_games_map[game.app_id] = game
