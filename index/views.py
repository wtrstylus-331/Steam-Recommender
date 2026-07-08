from os import environ
from django.http import HttpResponse, JsonResponse
from django.template import loader

dark_mode = True
def index(request):
    template = loader.get_template("test.html")

    # if request.method == "POST":
    #     dark_mode = not dark_mode

    context = {
        #"dark_mode": dark_mode,
    }
    return HttpResponse(template.render(context, request))

def test(request):
    return HttpResponse(environ.get("OPENAI_API_KEY"))

# def toggle_dark_mode(request):
#     global dark_mode
#     dark_mode = not dark_mode
#     return JsonResponse({"dark_mode": dark_mode})
