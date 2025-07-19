from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('send-message/', views.send_message, name='send_message'),
    path('conversations/', views.get_conversations, name='get_conversations'),
] 