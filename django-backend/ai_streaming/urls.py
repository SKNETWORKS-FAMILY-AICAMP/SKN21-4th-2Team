from django.urls import path
from . import views

app_name = 'ai_streaming'

urlpatterns = [
    path('', views.index, name='index'),
    path('create-session/', views.create_session, name='create_session'),
    path('get-messages/', views.get_session_messages, name='get_messages'),
    path('chat-stream/', views.chat_stream, name='chat_stream'),
    path('change-persona/', views.change_persona, name='change_persona'),
]
