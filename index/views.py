from django.http import HttpResponse, JsonResponse
from django.template import loader
from singletons.steam_web_api import SteamWebInstance
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
    return HttpResponse("profile stats")
