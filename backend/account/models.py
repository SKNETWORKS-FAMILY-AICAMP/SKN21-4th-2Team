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
    email = models.EmailField( # DB-varchar, python-str: Email유효성 검사를 한다.
        max_length=100,
        verbose_name="Email"
    )
    birthday = models.DateField( # DB: date 타입, python: datetime.date
        verbose_name="생일",
        null=True,  # Nullable 컬럼
        blank=True, # Form관련 설정. 빈 문자열(값)을 받을 수 있다. 
    )
    # 프로필 사진 - 이미지를 받는다.
    profile_img = models.ImageField(
        verbose_name="프로필 사진",
        null=True, # DB: NULL 허용컬럼
        blank=True,# Form: required=False
        upload_to="images/profile/%Y/%m/%d"
        # MEDIA_ROOT 아래 어디에 저장할 지 경로.
        # media\images\profile\업로드시점_년도\월\일
    )
    # uv pip install pillow
    # python manage.py  makemigrations, migrate


    def __str__(self):
        return f"username: {self.username}, name: {self.name}"

