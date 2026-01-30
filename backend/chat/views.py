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

from .models import Chat, Chat_Message
from .serializers import PostSerializer
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import transaction  # DB Transaction 처리.

from django.core.paginator import Paginator

from dotenv import load_dotenv

from django.shortcuts import render
from django.http import StreamingHttpResponse

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import trim_messages, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import traceback
load_dotenv()

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

def index(request):
    return render(request, 'chat/index.html')



class chat_session(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat_Message.objects.all()
    serializer_class = PostSerializer

def get_chain():

    prompt = ChatPromptTemplate(
        messages=[
            {
                "role": "system",
                "content": ("당신은 다양한 분야에 대해 전문적인 조언을 할 수 있는 유능한 인공지능 Assistant입니다."
                            "사용자의 질문에 대해 친절한 톤으로 답변해 주세요."
                            "답변의 난이도가 질문에 명시되어 있지 않은 경우, 해당 주제를 처음 접하는 사람도 이해할 수 있도록 단계적으로 차근차근 쉽게 설명해 주세요."
                            "확실하지 않은 내용은 단정하지 말고 그 한계를 명확히 밝혀 주세요.")
            },
            MessagesPlaceholder(variable_name="history"),
            {"role": "user", "content": "{input}"}
        ]
    )
    chat = ChatOpenAI(model_name="gpt-5-mini")
    return prompt | chat



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

    print(type(response)) # server를 실행한 터미널에 출력.
    return response

@permission_classes([AllowAny])
@api_view(['POST'])
def stream_chat(request):
    # 요청파라미터(GET방식)으로 사용자 질의를 받는다. "messages":"질의"
    message = request.GET.get('message', '')
    if not message:
        return StreamingHttpResponse("data: [ERROR] 메세지를 입력하세요.\n\n", content_type='text/event-stream')

    # Session 에서 대화히스토리(내역)을 저장. 없으면 만들어서(빈리스트)
    #   session에 저장.
    if 'message_history' not in request.session:
        request.session['message_history'] = []
        request.session.modified = True  # session상태가 변경됨을 표시
        request.session.save()  # 바뀐 상태를 저장/적용(보장)

    # LLM에 요청을하고 streaming으로 응답을 받아서 제공하는 generator
    def event_stream():
        try:
            message_history = request.session.get('message_history', [])

            chat = get_chain()
            ai_message = ""

            print(f"현재 히스토리: {len(message_history)}개 메시지")
            for chunk in chat.stream({"input": message, "history": message_history}):
                content = chunk.content.replace('\n', '<br>')
                if content:
                    ai_message += content
                    yield f"data: {content}\n\n"

            message_history.append(HumanMessage(content=message))
            message_history.append(AIMessage(content=ai_message.replace('<br>', '\n')))

            trimmed_msg = trim_messages(
                message_history,
                max_tokens=20,  # 최대 20개 메세지만 유지
                strategy="last",  # 최근 것을 남기는 전략
                token_counter=len,  # max_tokens를 계산하는 방법 -len:메세지 개수,
                start_on="human",  # 메세지목록의 시작 ROLE
                end_on=("human", "ai"),  # 메세지 목록의 마지막 ROLE
                include_system=True  # System프롬프트를 유지할 지 여부.
            )

            message_history_to_save = []
            # Session에 저장하기 위해서 HummanMessage/AIMessage 타입의 객체를
            # dictionary(OpenAI chat 형식)으로 변환해서 저장.
            for msg in trimmed_msg:
                if isinstance(msg, HumanMessage):
                    message_history_to_save.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    message_history_to_save.append({"role": "assistant", "content": msg.content})

            request.session['message_history'] = message_history_to_save
            request.session.modified = True
            request.session.save()

            print(f"저장된 히스토리: {len(message_history_to_save)}개 메시지")
            yield "data: [DONE]\n\n"

        except Exception as e:
            traceback.print_exc()
            yield f"data: [ERROR] {str(e)}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')  # iterable
    #  g=event_stream()
    #  for token in g:
    #     client에게 전송(token)

    response['Cache-Control'] = 'no-cache'


    return response