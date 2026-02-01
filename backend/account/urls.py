from django.contrib import admin
from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path("welcome", views.welcome, name="welcome"),
    path("create", views.create, name="create"),
    path("detail", views.detail, name='detail'),
    path("login", views.user_login, name="login"),
    path("logout", views.user_logout, name="logout"),
    path("update", views.update, name="update"),
    path("password_change", views.password_change, name="password_change"),
    path("delete", views.user_delete, name="delete"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
]

from django.urls import path



