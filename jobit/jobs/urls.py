from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("logout", views.view_logout, name="view_logout"),
    path("worker_profile", views.worker_profile, name="worker_profile"),
    path("settings", views.view_settings, name="settings"),
    path("get_skills", views.get_skills, name="get_skills"),
    path("add_skill", views.add_skill, name="add_skill"),
    path("listings", views.listings_view, name="listings"),
    path("listings/<int:id>", views.listing_details_view, name="listing_details"),
    path("listings/apply/<int:id>", views.apply, name="apply"),
    path("listings/add_listing", views.add_listing_view, name="add_listing"),
    path('remove-skill', views.remove_skill, name='remove_skill'),
    path('update_skill_level', views.update_skill_level, name='update_skill_level'),
    path('update_about_me', views.update_about_me, name='update_about_me'),
]