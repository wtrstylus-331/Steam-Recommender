import json

from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.template import loader

from instances.steam_profile import SteamProfileInstance
from instances.steam_web_api import SteamWebInstance, misc_app_details
from instances.openai_instance import OpenAIInstance, Models
import re, pprint

steam_profile_instance: SteamProfileInstance | None = None
ai_instance: OpenAIInstance = OpenAIInstance()
def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render({}, request))

def validate_url(request):
    url: str = request.GET.get("url", "")
    URL_PATTERN: str = r"(?:https|http):\/\/steamcommunity\.com\/(?:id|profiles)\/([a-zA-Z0-9-_\!\@\#\$\%\^\&\*\(\)\| ]+)\/{0,1}"
    ID_PATTERN: str = r"^^(?!https?:\/\/steamcommunity\.com\/(?:id|profiles)\/)[a-zA-Z0-9=\+\[\]\{\}\;\:\'\"\,\.\<\>\?\/\\\!\@\#\$\%\^\&\*\(\)\|\-_ ]+$"

    if not url:
        return JsonResponse({
            "valid_url": False,
            "steamid": None,
            "msg": "entry not found"
        })

    result_url = re.match(URL_PATTERN, url)
    result_id = re.match(ID_PATTERN, url)
    steam_instance = SteamWebInstance()
    steamid: int
    print(result_url)
    print(result_id)

    try:
        if result_url is not None:
            if result_url.groups()[0].isdigit():
                steamid = int(result_url.groups()[0])
            else:
                steamid = steam_instance.id_from_vanity_url(result_url.groups()[0])
            steam_instance.set_summary_from_id(steamid)
            steam_instance.set_steamid(steamid)
        elif result_id is not None:
            print(url)
            steamid = steam_instance.id_from_vanity_url(url)
            steam_instance.set_summary_from_id(steamid)
            steam_instance.set_steamid(steamid)
        else:
            return JsonResponse({
                "valid_url": False,
                "steamid": None,
                "msg": "invalid entry provided"
            })

        print(((steam_instance.profile_summary.get('response').get('players'))[0]).get('personastate'))

        return JsonResponse({
            "valid_url": True,
            "steamid": steamid,
            "message": "valid steam entry"
        })
    except Exception as e:
        return JsonResponse({"valid_url": False, "steamid": None, "message": str(e)})

def validate_id(request):
    id: str = request.GET.get("id", "")
    ID_PATTERN: str = r"^/^[a-zA-Z0-9-_\-\=\_\+\[\]\{\}\;\:\'\"\,\.\<\>\?\/\\\!\@\#\$\%\^\&\*\(\)\| ]+$/gm"

    if not id:
        return JsonResponse({
            "valid_id": False,
            "steamid": None,
            "msg": "id/display name not found"
        })

    result = re.match(ID_PATTERN, id)
    if not result:
        return JsonResponse({
            "valid_id": False,
            "steamid": None,
            "msg": "invalid steam id/display name provided"
        })

    steam_instance = SteamWebInstance()
    try:
        steamid = steam_instance.id_from_vanity_url(result.groups()[0])

        steam_instance.set_summary_from_id(steamid)
        steam_instance.set_steamid(steamid)
        print(((steam_instance.profile_summary.get('response').get('players'))[0]).get('personastate'))

        return JsonResponse({
            "valid_id": True,
            "steamid": steamid,
            "message": "valid steam id/display name"
        })
    except Exception as e:
        return JsonResponse({"valid_id": False, "steamid": None, "message": str(e)})

def sort_games(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            global steam_profile_instance

            match data.get("type"):
                case 'playtime-descending':
                    steam_profile_instance.sort_games_by_playtime(descending=True)
                case 'playtime-ascending':
                    steam_profile_instance.sort_games_by_playtime(descending=False)
                case 'name':
                    steam_profile_instance.sort_games_by_name()
                case default:
                    return JsonResponse({"error": "Improper sort type requested", "sorted": False}, status=400)

            games_json = [
                {
                    "app_id": g.app_id,
                    "app_name": g.app_name,
                    "playtime_forever_hrs": g.playtime_forever_hrs,
                    "capsule_hash": g.app_capsule_hash,
                    "capsule_file_name": g.capsule_file_name,
                }
                for g in steam_profile_instance.get_games()
            ]
            #print(games_json)

            return JsonResponse({"sorted": True, "games": games_json}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON", "sorted": False}, status=400)
    return JsonResponse({"error": "Invalid request method", "sorted": False}, status=405)

def lazyload_games(request):
    #if request.method == "POST":
    try:
        global steam_profile_instance
        print(steam_profile_instance is None)

        games_json = [
            {
                "app_id": g.app_id,
                "app_name": g.app_name,
                "playtime_forever_hrs": g.playtime_forever_hrs,
                "capsule_hash": g.app_capsule_hash,
                "capsule_file_name": g.capsule_file_name,
            }
            for g in steam_profile_instance.get_to_lazyload()
        ]

        return JsonResponse({"sorted": True, "games": games_json}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON", "sorted": False}, status=400)
    #return JsonResponse({"error": "Invalid request method", "sorted": False}, status=405)

def set_model(request):
    try:
        data = json.loads(request.body)
        model = data.get("model")
        global ai_instance

        if model in Models:
            ai_instance.model = model
            return JsonResponse({"response": True}, status=200)
        else:
            return JsonResponse({"response": False}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON", "response": False}, status=400)

def faq(request):
    template = loader.get_template("faq.html")
    return HttpResponse(template.render({}, request))

def profile(request):
    template = loader.get_template("profile_page.html")
    steam_instance = SteamWebInstance()
    global steam_profile_instance
    steam_profile_instance = SteamProfileInstance()

    if not steam_instance.session_steamid:
        return index(request)

    steam_profile_instance.set_profile(steam_instance.profile_summary)
    games = steam_instance.get_user_owned_games(steam_profile_instance.steam_profile_id)
    steam_profile_instance.set_games(games)

    is_playing: int = (1 if steam_profile_instance.personaState is 1
                           and steam_profile_instance.playingGameId is not None else 0)

    context = {
        'steam_id': steam_profile_instance.steam_profile_id,
        'persona_name': steam_profile_instance.steam_profile_name,
        'persona_state': steam_profile_instance.personaState,
        'is_playing_game': is_playing,
        'avatar_url': steam_profile_instance.steam_avatar_url,
        'games_list': steam_profile_instance.get_games(),
        'recent_games_list': steam_profile_instance.displayed_recent_games,
        'game_count': steam_profile_instance.steam_game_count,
        'recent_game_count': steam_profile_instance.recent_game_count,
        'openai_key_found': 1 if ai_instance.get_api_key() is not None else 0
    }
    return HttpResponse(template.render(context, request))

def get_user_status(request):
    try:
        steam_instance = SteamWebInstance()
        profile_summary = steam_instance.get_summary_from_id(steam_instance.session_steamid)

        details = profile_summary["response"]["players"][0]

        return JsonResponse({
            "personaState": details.get("personastate"),
            "playingGameId": details.get("gameid")
        })
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON", "personaState": None, "playingGameId": None}, status=400)

def generate_summary(request):
    if request.method == "GET":
        try:
            recent_details: list[dict] = [
                misc_app_details(x)
                for x in steam_profile_instance.displayed_recent_games if x.get_playtime_hrs() > 1.0
            ]

            return JsonResponse({"response": False}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON", "response": False}, status=400)
    return JsonResponse({"error": "Invalid request method", "response": False}, status=405)

def send_message(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = ai_instance.send_message(data.get("prompt"))

            return StreamingHttpResponse(
                message,
                content_type="text/plain"
            , status=200)

            #return JsonResponse({"response": message}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON", "response": False}, status=400)
    return JsonResponse({"error": "Invalid request method", "response": False}, status=405)
