from django.http import HttpResponse, JsonResponse
from django.template import loader

from instances.steam_profile import SteamProfileInstance
from instances.steam_web_api import SteamWebInstance, misc_app_details
import re, pprint
def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render({}, request))

def validate_url(request):
    url: str = request.GET.get("url", "")
    URL_PATTERN: str = r"(?:https|http):\/\/steamcommunity\.com\/(?:id|profiles)\/([a-zA-Z0-9]+)\/{0,1}"

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
        request.session["steamid"] = steamid
        return JsonResponse({
            "valid_url": True,
            "steamid": steamid,
            "message": "valid steam url"
        })
    except Exception as e:
        return JsonResponse({"valid_url": False, "steamid": None, "message": str(e)})

def faq(request):
    template = loader.get_template("faq.html")
    return HttpResponse(template.render({}, request))

def profile(request):
    steamid = request.session["steamid"]
    template = loader.get_template("profile_page.html")
    steam_profile_instance = SteamProfileInstance()

    if not steamid:
        return index(request)

    steam_profile_instance.set_profile(SteamWebInstance().profile_summary)

    if steam_profile_instance.steam_profile_id:
        steam_profile_instance.set_games(SteamWebInstance().get_user_owned_games(steam_profile_instance.steam_profile_id))

    context = {
        'steam_id': steam_profile_instance.steam_profile_id,
        'persona_name': steam_profile_instance.steam_profile_name,
        'avatar_url': steam_profile_instance.steam_avatar_url,
        'games_list': steam_profile_instance.get_games(),
        'game_count': steam_profile_instance.steam_game_count,
        'recent_game_count': steam_profile_instance.recent_game_count
    }
    return HttpResponse(template.render(context, request))
