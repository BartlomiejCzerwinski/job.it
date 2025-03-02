from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("get-current-user", views.get_current_user, name="get-current-user"),
    path("remove-skill", views.remove_skill, name="remove-skill"),
]