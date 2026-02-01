from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

class CustomUser(AbstractUser):
    user_id = models.CharField(max_length=255, unique=True)
    nickname = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Removed default value

    REQUIRED_FIELDS = ['nickname', 'name']
    USERNAME_FIELD = 'user_id'

    def __str__(self):
        return self.nickname



