from os import getenv
from django.http import HttpResponse, JsonResponse
from django.template import loader
from dotenv import load_dotenv
def index(request):
    template = loader.get_template("test.html")

    # if request.method == "POST":
    #     dark_mode = not dark_mode

    context = {
        #"dark_mode": dark_mode,
    }
    return HttpResponse(template.render(context, request))

def test(request):
    load_dotenv()
    #return HttpResponse(getenv("OPENAI_API_KEY"))
    return HttpResponse(getenv("STEAM_WEB_API_KEY"))
    return HttpResponse(environ.get("OPENAI_API_KEY"))

# def toggle_dark_mode(request):
#     global dark_mode
#     dark_mode = not dark_mode
#     return JsonResponse({"dark_mode": dark_mode})
