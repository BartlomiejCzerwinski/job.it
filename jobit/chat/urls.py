from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('init-conversation/', views.init_conversation, name='init_conversation'),
    path('send-message/', views.send_message, name='send_message'),
    path('conversations/', views.get_conversations, name='get_conversations'),
    path('conversations/<int:conversation_id>/messages/', views.get_messages, name='get_messages'),
    path('notifications/', views.get_notifications, name='get_notifications'),
] 