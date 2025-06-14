from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("get-current-user", views.get_current_user, name="get-current-user"),
    path("remove-skill", views.remove_skill, name="remove-skill"),
    path("social-links", views.get_social_links, name="get-social-links"),
    path("social-links/add", views.add_social_link, name="add-social-link"),
    path("social-links/<int:link_id>", views.update_social_link, name="update-social-link"),
    path("social-links/<int:link_id>/delete", views.delete_social_link, name="delete-social-link"),
    path("update-position", views.update_position, name="update-position"),
    path("update-location", views.update_location, name="update-location"),
    path("projects/add", views.add_project, name="add-project"),
    path('projects/delete/<int:project_id>', views.delete_project, name='delete_project'),
    path('projects/update/<int:project_id>', views.update_project, name='update_project'),
    path('logout/', views.logout_user, name='logout'),
    path('profile-photo/remove/', views.remove_profile_photo, name='remove_profile_photo'),
    path('profile-photo/add/', views.add_profile_photo, name='add_profile_photo'),
    path('profile-photo/<int:user_id>/', views.get_profile_photo, name='get_profile_photo'),
]