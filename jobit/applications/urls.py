from django.urls import path

from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<int:job_id>/', views.apply, name='apply'),
]