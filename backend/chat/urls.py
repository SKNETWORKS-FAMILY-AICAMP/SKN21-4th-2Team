from django.contrib import admin
from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path("welcome", views.welcome, name="welcome"),
    path("chatting", views.chatting.as_view(), name="chatting"),
    path("chat_session", views.chat_session.as_view(), name="chat_session"),
    
    # RAG 채팅 API 엔드포인트
    path("api/chat/", views.ChatAPIView.as_view(), name="chat_api"),
    path("api/chat/stream/", views.StreamingChatAPIView.as_view(), name="chat_stream"),
    path("api/counselors/", views.CounselorListView.as_view(), name="counselors"),
    
    # 상담사 통계 API 엔드포인트
    path("api/counselor-stats/", views.CounselorStatsView.as_view(), name="counselor_stats"),
    path("api/counselor-select/", views.CounselorSelectView.as_view(), name="counselor_select"),
]
