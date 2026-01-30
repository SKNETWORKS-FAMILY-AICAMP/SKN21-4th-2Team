"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from chat import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path('admin/', admin.site.urls),
    # 1. ip:포트번호 이후, client의 요청경로 2. 호출할 view, 3. name="설정 이름"
    # path('polls/welcome', welcome, name="poll_welcome")

    # polls/ 로 시작하는 url 경로로 요청이 들어오면 polls앱/urls.py 의 설정으로 가서 나머지를 확인.
    path("chat/", include("chat.urls")),
    path("account/", include("account.urls")),

]

