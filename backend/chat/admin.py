from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Chat, Chat_Message
from django.urls import path, include

chat_object = Chat
Chat_Message_object = Chat_Message
# admin.site.register(chat, Chat_Message)
admin.site.register(chat_object)
admin.site.register(Chat_Message_object)