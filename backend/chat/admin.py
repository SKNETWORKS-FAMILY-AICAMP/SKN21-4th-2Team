from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from .models import Chat, Chat_Message

admin.site.register(Chat, Chat_Message)