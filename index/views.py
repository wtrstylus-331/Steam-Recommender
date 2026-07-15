from django.http import HttpResponse, JsonResponse
from django.template import loader
from singletons.steam_web_api import SteamWebInstance
import re, pprint

# def index(request):
#     url: str = request.GET.get("url", "")
#     URL_PATTERN: str = r"(?:https|http):\/\/steamcommunity\.com\/(?:id|profiles)\/([a-zA-Z0-9]+)\/{0,1}"
#     #print(url)
#
#     if url:
#         result = re.match(URL_PATTERN, url)
#         steam_instance = SteamWebInstance()
#         if result:
#             steamid: int
#             if result.groups()[0].isdigit():
#                 steamid = int(result.groups()[0])
#             else:
#                 response = dict(steam_instance.id_from_vanity_url(str(result.groups()[0])))
#                 pprint.pprint(response)
#
#                 steamid = int(dict(response['response'])['steamid'])
#
#             #game_info = steam_instance.get_user_owned_games(steamid)
#
#             #pprint.pprint(game_info['response']['game_count'])
#             pprint.pprint(
#                 steam_instance.get_summary_from_id(
#                     steamid
#                 )
#             )
#
#             return HttpResponse(f"profile url: {url}, steamid: {str(steamid)}")
#             #return HttpResponse(f"profile url: {result.groups()[0]}")
#         else:
#             return HttpResponse(f"profile url: None")
#     else:
#         template = loader.get_template("index.html")
#         return HttpResponse(template.render({}, request))

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
        return JsonResponse({"valid": False, "message": str(e)})

def index_url_valid(request):
    pass

def faq(request):
    template = loader.get_template("faq.html")
    context = {
    }
    return HttpResponse(template.render(context, request))
    # from singletons.openai_key import OpenAIKey
    # return HttpResponse(OpenAIKey.api_key)

def test(request):
    url = request.GET.get("url", "")
    return HttpResponse(f"profile url: {url}")


# def test(request):
#     load_dotenv()
#     #return HttpResponse(getenv("OPENAI_API_KEY"))
#     return HttpResponse(getenv("STEAM_WEB_API_KEY"))
#     return HttpResponse(environ.get("OPENAI_API_KEY"))

# def toggle_dark_mode(request):
#     global dark_mode
#     dark_mode = not dark_mode
#     return JsonResponse({"dark_mode": dark_mode})
