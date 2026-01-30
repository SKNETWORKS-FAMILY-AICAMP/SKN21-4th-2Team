# polls/models.py
#  모델 클래스들을 정의
from django.db import models
from account.models import CustomUser
# from chat.models import Role
import uuid

# 모델 클래스 정의 - Question(설문질문) - Choice(설문의 보기)
## 1. models.Model을 상속
## 2. class 변수로 Field들을 정의: 
#                     Field == DB column, Model객체의 Instance 변수 이 둘에 대한 설정

# Model class 정의 할 때 primary key Field를 선언하지 않으면, 
class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    session_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.id}. {self.user_id}. {self.session_id}. {self.is_active}. {self.created_at}"


# 보기 테이블
class Role(models.Model):

    role_id = models.AutoField(primary_key=True)
    role = models.CharField(unique=True, max_length=50) # 문자열타입 (user 또는 상담사 이름)

    def __str__(self):
        return f"{self.role_id}. {self.role}"

# 보기 테이블
class Chat_Message(models.Model):

    message_id = models.AutoField(primary_key=True)
    role_id = models.ForeignKey(
        Role, # 참조할 Model Class
        on_delete=models.DO_NOTHING
    )
    message = models.TextField() # 긴 문자열 타입
    session_id = models.ForeignKey(
        Chat, # 참조할 Model Class
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message_id}. {self.role}. {self.message}. {self.session_id}. {self.created_at}"

# create table choice(
#     choice_text varchar(200) not null,
#     votes int not null default 0,
#     question int,
#     constraint q_fk foreign key (question) references QUESTION(id) on delete cascade
# )


# 모델 클래스 정의 한 후에 Database에 적용
# Project Root >   python manage.py makemigrations         # 모든 app들에 적용
#                  python manage.py makemigrations  polls  # polls app에 만 적용
#     -> table에 적용(생성, 수정) 할 코드를 작성.

#  python manage.py migrate  # DB에 적용(table생성, 수정)

# python  manage.py  inspectdb > a.py
