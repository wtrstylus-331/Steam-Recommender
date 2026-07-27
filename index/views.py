import json

from django.http import HttpResponse, JsonResponse
from django.template import loader

from instances.steam_profile import SteamProfileInstance
from instances.steam_web_api import SteamWebInstance
from instances.openai_instance import OpenAIInstance
import re, pprint

steam_profile_instance: SteamProfileInstance | None = None
def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render({}, request))

def validate_url(request):
    url: str = request.GET.get("url", "")
    URL_PATTERN: str = r"(?:https|http):\/\/steamcommunity\.com\/(?:id|profiles)\/([a-zA-Z0-9-]+)\/{0,1}"

    if not url:
        return JsonResponse({
            "valid_url": False,
            "steamid": None,
            "msg": "url not found"
        })

    result = re.match(URL_PATTERN, url)
    if not result:
        return JsonResponse({
            "valid_url": False,
            "steamid": None,
            "msg": "invalid steam url format provided"
        })

    steam_instance = SteamWebInstance()
    try:
        if result.groups()[0].isdigit():
            steamid = int(result.groups()[0])
        else:
            steamid = steam_instance.id_from_vanity_url(result.groups()[0])

        steam_instance.set_summary_from_id(steamid)
        steam_instance.set_steamid(steamid)

        return JsonResponse({
            "valid_url": True,
            "steamid": steamid,
            "message": "valid steam url"
        })
    except Exception as e:
        return JsonResponse({"valid_url": False, "steamid": None, "message": str(e)})

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
    if request.method == "POST":
        try:
            global steam_profile_instance

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
    return JsonResponse({"error": "Invalid request method", "sorted": False}, status=405)

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

    context = {
        'steam_id': steam_profile_instance.steam_profile_id,
        'persona_name': steam_profile_instance.steam_profile_name,
        'avatar_url': steam_profile_instance.steam_avatar_url,
        'games_list': steam_profile_instance.get_games(),
        'recent_games_list': steam_profile_instance.displayed_recent_games,
        'game_count': steam_profile_instance.steam_game_count,
        'recent_game_count': steam_profile_instance.recent_game_count,
        'openai_key_found': 1 if OpenAIInstance().api_key is not None else 0
    }
    return HttpResponse(template.render(context, request))
