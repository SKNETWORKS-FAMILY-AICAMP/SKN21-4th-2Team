from django.db import models
from django.contrib.auth.models import AbstractUser
# 기존 Django에서 제공하는 User모델을 확장해서 정의 - AbstractUser상속해서 구현

# AbstractUser -> username, password
# CustomUser:  추가할 field들 정의 (name, email, birthday, [profile_image])
class CustomUser(AbstractUser):

    name = models.CharField(
        max_length=100,
        verbose_name="이름"# Form 관련 설정. 
                           # ModelForm을 만들 경우 form field 설정을 Model field에 한다.
    )
    # urls = models.JSONField(null=True, blank=True)
    # uv pip install pillow
    # python manage.py  makemigrations, migrate


    def __str__(self):
        return f"username: {self.username}, nickname: {self.name}"

