from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    #path("", views.index, name="url_input"), # works
    path("faq/", views.faq, name="faq"),
    #path("toggle/", views.toggle_dark_mode, name="toggle_dark_mode"),
]
