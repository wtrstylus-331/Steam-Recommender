from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("profile/", views.profile, name="profile"),
    path("faq/", views.faq, name="faq"),
    path("validate/", views.validate_url, name="validate_url"), #private request
    path("sortgames/", views.sort_games, name="sortgames"), #private request
    path("lazyload/", views.lazyload_games, name="lazyload"), #private request
]
