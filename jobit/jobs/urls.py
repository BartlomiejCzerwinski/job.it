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
    path("listings/add_listing", views.add_listing_view, name="add_listing"),
    path("listings/<int:listing_id>/close", views.close_listing, name="close_listing"),
    path("listings/<int:listing_id>/archive", views.archive_listing, name="archive_listing"),
    path("listings/<int:listing_id>/reactivate", views.reactivate_listing, name="reactivate_listing"),
    path('remove-skill', views.remove_skill, name='remove_skill'),
    path('update_skill_level', views.update_skill_level, name='update_skill_level'),
    path('update_about_me', views.update_about_me, name='update_about_me'),
    path('update_first_name', views.update_first_name, name='update_first_name'),
    path('update_last_name', views.update_last_name, name='update_last_name'),
    path('update_email', views.update_email, name='update_email'),
    path('update_mobile', views.update_mobile, name='update_mobile'),
    path('update_starts_in', views.update_starts_in, name='update_starts_in'),
    path('search', views.search_results_view, name='search_results'),
]