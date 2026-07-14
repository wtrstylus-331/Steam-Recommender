# main web instance for inputted profile to display game inventory, stats, etc.
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
    steam_id: int
    steam_name: str
    steam_avatar_url: str
    steam_games: list[SteamGame]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SteamProfileInstance, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.steam_profile_id = None
        self.steam_profile_name = None
        self.steam_avatar_url = ""
        self.steam_games = []

        self._initialized = True

    def set_profile(self, response: dict) -> None:
        """Take in raw dictionary <response> from the WebAPI call
        from ValvePython and set instance attributes"""

        details: dict = response["response"]["players"][0]
        self.steam_profile_id = int(details["steamid"])
        self.steam_profile_name = details["personaname"]
        self.steam_avatar_url = details["avatarfull"]

    def add_game(self, game: SteamGame) -> None:
        self.steam_games.append(game)
        self.steam_games.sort(key=lambda x: x.app_name, reverse=False)
