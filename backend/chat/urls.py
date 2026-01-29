from django.contrib import admin
from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path("welcome", views.welcome, name="welcome"),
    path('stream/', views.stream_chat, name='stream_chat'),
    path('', views.index, name='index'),
    #path("chatting", views.chatting.as_view(), name="chatting"),
    #path("chat_session", views.chat_session.as_view(), name="chat_session")
]
