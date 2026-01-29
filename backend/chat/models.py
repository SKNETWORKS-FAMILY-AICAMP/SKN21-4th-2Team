# polls/models.py
#  모델 클래스들을 정의
from django.db import models
from account.models import CustomUser
import uuid

# 모델 클래스 정의 - Question(설문질문) - Choice(설문의 보기)
## 1. models.Model을 상속
## 2. class 변수로 Field들을 정의: 
#                     Field == DB column, Model객체의 Instance 변수 이 둘에 대한 설정

# Model class 정의 할 때 primary key Field를 선언하지 않으면, 
class Chat(models.Model):
    # Field 정의: 변수명-(instance변수명, column 이름)
    #             Field 객체를 할당. Field객체 - column 설정(type, null허용여부,..)
    username = models.ForeignKey(
        CustomUser, # 참조할 Model Class
        on_delete=models.CASCADE # 참조 값이 삭제 된 경우 어떻게 할지 -> cascade: 삭제
    ) #   
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    # DateTimeField: 일시타입(datetime, datetime.datetime)
    # auto_now_add: insert 될 때 일시를 자동 입력.
    created_at = models.DateTimeField(auto_now_add=True)
    # urls = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.username}. {self.session_id}. {self.is_active}. {self.created_at}"

    # create table question(
    #     question_text varchar(200),
    #     pub_date datetime current_timestamp
    # )

# 보기 테이블
class Chat_Message(models.Model):

    message_id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=10) # 문자열타입 (user 또는 assistant)
    message = models.TextField() # 긴 문자열 타입
    session_id = models.ForeignKey(
        Chat, # 참조할 Model Class
        on_delete=models.CASCADE # 참조 값이 삭제 된 경우 어떻게 할지 -> cascade: 삭제
        # , related_name="my_choice" # q.my_choice.all()
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # urls = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.message_id}. {self.role}. {self.message}. {self.session_id}. {self.created_at}"

# 보기 테이블
class Persona(models.Model):

    persona_id = models.CharField(max_length=10)
    youtuber_name = models.CharField(max_length=10) # 문자열타입 (user 또는 assistant)

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
