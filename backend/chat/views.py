import os
import sys

# 프로젝트 루트 디렉토리를 sys.path에 추가
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse 

from .models import Chat, Chat_Message, CounselorStats
from .serializers import PostSerializer, ChatRequestSerializer, ChatResponseSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.core.paginator import Paginator

from datetime import datetime

# RAG 모듈 임포트
from rag.retriever.logic import operate_retriever
from rag.chain.pipeline import init_llm, create_chain
from rag.prompts.templates import get_persona_prompt, PERSONA_FILE_MAP
from langchain_core.runnables import RunnableLambda


# 글로벌 LLM/Retriever 캐싱 (싱글톤)
_llm = None
_retriever = None


def get_llm():
    """LLM 인스턴스 반환 (싱글톤)"""
    global _llm
    if _llm is None:
        _llm = init_llm()
        print("✓ LLM 초기화 완료")
    return _llm


def get_retriever():
    """Retriever 인스턴스 반환 (싱글톤)"""
    global _retriever
    if _retriever is None:
        _retriever = RunnableLambda(lambda q: operate_retriever(q, k=5) or [])
        print("✓ Retriever 초기화 완료")
    return _retriever


# =====================================================
# 기존 DRF Views
# =====================================================

class chatting(generics.ListCreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = PostSerializer


class chat_session(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat_Message.objects.all()
    serializer_class = PostSerializer


# =====================================================
# RAG 채팅 API Views
# =====================================================

class CounselorListView(APIView):
    """GET /api/counselors/ - 상담사 목록 반환"""
    
    def get(self, request):
        counselors = [
            {"id": name, "name": name}
            for name in PERSONA_FILE_MAP.keys()
            if PERSONA_FILE_MAP[name] is not None
        ]
        return Response({"counselors": counselors})


# =====================================================
# 상담사 통계 API Views
# =====================================================

class CounselorStatsView(APIView):
    """GET /api/counselor-stats/ - 상담사 선택 통계 조회"""
    
    def get(self, request):
        stats = CounselorStats.objects.all()
        data = [
            {
                "name": s.counselor_name,
                "count": s.selection_count,
                "last_selected": s.last_selected.isoformat() if s.last_selected else None
            }
            for s in stats
        ]
        return Response({"stats": data})


class CounselorSelectView(APIView):
    """POST /api/counselor-select/ - 상담사 선택 시 카운트 증가"""
    
    def post(self, request):
        counselor_name = request.data.get('counselor_name')
        if not counselor_name:
            return Response(
                {"error": "counselor_name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 상담사 통계 업데이트 (없으면 생성)
        stats, created = CounselorStats.objects.get_or_create(
            counselor_name=counselor_name
        )
        stats.selection_count += 1
        stats.save()
        
        return Response({
            "status": "success",
            "counselor_name": counselor_name,
            "count": stats.selection_count
        })


class ChatAPIView(APIView):
    """POST /api/chat/ - RAG 기반 채팅 응답"""
    
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.validated_data['question']
        youtuber_name = serializer.validated_data['youtuber_name']
        
        try:
            # 1. 유튜버 이름 검증
            if youtuber_name not in PERSONA_FILE_MAP:
                # 비슷한 이름 찾기
                for name in PERSONA_FILE_MAP.keys():
                    if youtuber_name in name or name in youtuber_name:
                        youtuber_name = name
                        break
                else:
                    youtuber_name = "김달"
            
            if PERSONA_FILE_MAP.get(youtuber_name) is None:
                return Response(
                    {"error": f"'{youtuber_name}' 상담사는 아직 준비되지 않았습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 2. LLM, Retriever, Prompt 준비
            llm = get_llm()
            retriever = get_retriever()
            prompt = get_persona_prompt(youtuber_name=youtuber_name)
            
            # 3. Chain 생성 및 실행
            chain = create_chain(llm, retriever, prompt)
            response_text = chain.invoke(question)
            
            return Response({
                "answer": response_text,
                "youtuber_name": youtuber_name,
                "status": "success"
            })
            
        except Exception as e:
            print(f"❌ 채팅 처리 중 오류: {e}")
            return Response(
                {"error": f"응답 생성 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StreamingChatAPIView(APIView):
    """POST /api/chat/stream/ - 스트리밍 채팅 응답"""
    
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.validated_data['question']
        youtuber_name = serializer.validated_data['youtuber_name']
        
        try:
            # 1. 유튜버 이름 검증
            if youtuber_name not in PERSONA_FILE_MAP:
                for name in PERSONA_FILE_MAP.keys():
                    if youtuber_name in name or name in youtuber_name:
                        youtuber_name = name
                        break
                else:
                    youtuber_name = "김달"
            
            if PERSONA_FILE_MAP.get(youtuber_name) is None:
                return Response(
                    {"error": f"'{youtuber_name}' 상담사는 아직 준비되지 않았습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 2. LLM, Retriever, Prompt 준비
            llm = get_llm()
            retriever = get_retriever()
            prompt = get_persona_prompt(youtuber_name=youtuber_name)
            
            # 3. Chain 생성
            chain = create_chain(llm, retriever, prompt)
            
            # 4. 스트리밍 응답 생성
            def generate():
                for chunk in chain.stream(question):
                    yield chunk
            
            return StreamingHttpResponse(
                generate(),
                content_type='text/plain; charset=utf-8'
            )
            
        except Exception as e:
            print(f"❌ 스트리밍 처리 중 오류: {e}")
            return Response(
                {"error": f"응답 생성 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =====================================================
# 기존 Template View
# =====================================================

def welcome(request):
    print("welcome 실행")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = render(
        request,
        "chat/welcome.html",
        {"now": now}
    )
    print(type(response))
    return response