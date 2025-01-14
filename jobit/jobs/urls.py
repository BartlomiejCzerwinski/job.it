from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("logout", views.view_logout, name="view_logout"),
    path("/worker_profile", views.worker_profile, name="worker_profile")
]