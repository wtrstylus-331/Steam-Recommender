from django.http import HttpResponse, JsonResponse
from django.template import loader

from singletons.steam_profile import SteamProfileInstance
from singletons.steam_web_api import SteamWebInstance, genres_from_appid
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

        SteamProfileInstance().set_profile(steam_instance.get_summary_from_id(steamid))
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
    template = loader.get_template("profile_page.html")
    profile_inst = SteamProfileInstance()

    if profile_inst.steam_profile_id:
        profile_inst.set_games(SteamWebInstance().get_user_owned_games(profile_inst.steam_profile_id))

    context = {
        'steam_id': profile_inst.steam_profile_id,
        'persona_name': profile_inst.steam_profile_name,
        'avatar_url': profile_inst.steam_avatar_url,
        'games_list': profile_inst.get_games(),
        'game_count': profile_inst.steam_game_count
    }
    return HttpResponse(template.render(context, request))
