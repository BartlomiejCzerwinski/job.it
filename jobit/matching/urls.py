from django.urls import path

from . import views

urlpatterns = [
    path('knn-match/', views.knn_match, name='knn_match'),
    path('chat/', views.chat_endpoint, name='chat_endpoint'),
]