from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("test/", views.test, name="test"), # works
    path("faq/", views.faq, name="faq"),
    #path("toggle/", views.toggle_dark_mode, name="toggle_dark_mode"),
]
