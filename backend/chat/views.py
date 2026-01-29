
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse 

from .models import Chat, Chat_Message
from .serializers import PostSerializer
from rest_framework import generics
from django.db import transaction  # DB Transaction 처리.
from django.core.paginator import Paginator

from datetime import datetime

# Create your views here.

class chatting(generics.ListCreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = PostSerializer

class chat_session(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat_Message.objects.all()
    serializer_class = PostSerializer


# 설문 welcome page view
#  요청 -> 인삿말 화면을 응답.
def welcome(request):
    print("welcome 실행")
    # 요청 처리
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 응답 화면 생성 -> template 호출(template이 사용할 값을 전달-now)
    response = render( # template 호출 -결과-> HttpResponse로 반환
        request, # HttpRequest
        "chat/welcome.html", # 호출할 template의 경로
        {"now":now} # template에 전달할 값들. name-value 전달.
                    # Context Value 라고 한다.
    )
    print(type(response)) # server를 실행한 터미널에 출력.
    return response