from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.urls import path, include

CustomUser_object = CustomUser
admin.site.register(CustomUser_object)