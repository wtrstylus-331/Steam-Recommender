from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("validate/", views.validate_url, name="validate_url"),
    path("sortgames/", views.sort_games, name="sortgames"),
    path("profile/", views.profile, name="profile"),
    #path("", views.index, name="url_input"), # works
    path("faq/", views.faq, name="faq"),
    #path("toggle/", views.toggle_dark_mode, name="toggle_dark_mode"),
]
