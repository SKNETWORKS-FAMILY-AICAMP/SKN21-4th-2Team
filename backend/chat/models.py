
from django.db import models
from account.models import CustomUser
import uuid

class Chat(models.Model):
    # Field 정의: 변수명-(instance변수명, column 이름)
    #             Field 객체를 할당. Field객체 - column 설정(type, null허용여부,..)
    username = models.ForeignKey(
        CustomUser, # 참조할 Model Class
        on_delete=models.CASCADE, # 참조 값이 삭제 된 경우 어떻게 할지 -> cascade: 삭제
        related_name='chat_chats' # q.my_choice.all()
    ) #   
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    # DateTimeField: 일시타입(datetime, datetime.datetime)
    # auto_now_add: insert 될 때 일시를 자동 입력.
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.session_id)

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

    def __str__(self):
        return f"{self.message_id}. {self.role}. {self.message}. {self.session_id}. {self.created_at}"