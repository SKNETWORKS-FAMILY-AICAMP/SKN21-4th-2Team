# polls/views.py

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse 
# url conf의 설정 이름으로 url을 조회하는 함수
## path("url", view함수, name='name')
# reverse("name") => url

from django.db import transaction  # DB Transaction 처리.
from django.core.paginator import Paginator

from datetime import datetime
# from .models import Question, Choice

# Create your views here.

# 설문 welcome page view
#  요청 -> 인삿말 화면을 응답.
def welcome(request):
    print("welcome 실행")
    # 요청 처리
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 응답 화면 생성 -> template 호출(template이 사용할 값을 전달-now)
    response = render( # template 호출 -결과-> HttpResponse로 반환
        request, # HttpRequest
        "account/welcome.html", # 호출할 template의 경로
        {"now":now} # template에 전달할 값들. name-value 전달.
                    # Context Value 라고 한다.
    )
    print(type(response)) # server를 실행한 터미널에 출력.
    return response