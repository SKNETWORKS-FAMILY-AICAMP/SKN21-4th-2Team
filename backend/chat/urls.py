from django.contrib import admin
from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path("welcome", views.welcome, name="welcome"),
    path("chatting/", views.chatting.as_view(), name="chatting"),
    path("chat_session/", views.chat_session.as_view(), name="chat_session"),
    path("stream/", views.stream, name="stream"),
    path("history/", views.ChatHistoryView.as_view(), name="chat-history"),
    path("history/<uuid:session_id>/", views.ChatMessageListView.as_view(), name="chat-messages"),
]
