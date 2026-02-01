
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse 

from .models import Chat, Chat_Message
from .serializers import PostSerializer, ChatSerializer, ChatMessageSerializer
from rest_framework import generics, permissions
from django.db import transaction  # DB Transaction 처리.
from django.core.paginator import Paginator
from datetime import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class chatting(generics.ListCreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer # Changed from PostSerializer

    def post(self, request, *args, **kwargs):
        print("=== Chatting View POST ===")
        print(f"Data: {request.data}")
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            print("Error in chatting view:")
            traceback.print_exc()
            raise e

@method_decorator(csrf_exempt, name='dispatch')
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

# RAG Streaming Implementation
import json
import sys
from pathlib import Path
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# Add project root to sys.path to allow importing from 'rag'
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

try:
    from rag.chain.pipeline import init_llm, create_chain
    from rag.retriever.logic import operate_retriever
    from rag.prompts.templates import get_persona_prompt, PERSONA_FILE_MAP
    from langchain_core.runnables import RunnableLambda
except ImportError as e:
    print(f"Error importing RAG modules: {e}")

import traceback
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny]) # CSRF exemption for now, but we verify user manually
def stream(request):
    print("=== Stream View Started ===")
    try:
        user = request.user
        print(f"User: {user}, Auth: {user.is_authenticated}")

        # Use request.data for DRF views, request.body raises RawPostDataException if data stream already read
        data = request.data
        print(f"Request Data: {data}")

        question = data.get('question')
        youtuber_name = data.get('youtuber_name', '김달')
        session_id = data.get('session_id') 
        
        # Validating youtuber_name
        if youtuber_name not in PERSONA_FILE_MAP:
             print(f"Invalid youtuber_name '{youtuber_name}', defaulting to '김달'")
             youtuber_name = '김달'

        # Chat Session Handling
        chat_obj = None
        print(f"Handling Chat Session. Session ID provided: {session_id}")
        
        try:
            if user.is_authenticated:
                if session_id:
                    try:
                        chat_obj = Chat.objects.get(session_id=session_id, username=user)
                        print(f"Retrieved existing chat session: {chat_obj.session_id}")
                    except Chat.DoesNotExist:
                        chat_obj = Chat.objects.create(username=user)
                        print(f"Created new chat session (invalid/missing ID): {chat_obj.session_id}")
                else:
                    chat_obj = Chat.objects.create(username=user)
                    print(f"Created new chat session: {chat_obj.session_id}")
                
                # Save User Message
                if chat_obj:
                    msg = Chat_Message.objects.create(session_id=chat_obj, role='user', message=question)
                    print(f"Saved User Message: PK={msg.pk}")
        except Exception as e:
            print("Error during DB operations:")
            traceback.print_exc()
            # Continue without DB if DB fails? Or fail?
            # Let's continue for now to see if LLM works
            
        print("Initializing LLM...")
        try:
            llm = init_llm()
            retriever = RunnableLambda(lambda q: operate_retriever(q, k=5) or [])
            prompt = get_persona_prompt(youtuber_name=youtuber_name)
            chain = create_chain(llm, retriever, prompt)
            print("LLM Chain created successfully")
        except Exception as e:
            print("Error initializing RAG components:")
            traceback.print_exc()
            return StreamingHttpResponse(f"RAG Init Error: {str(e)}", status=500)

        def event_stream():
            full_answer = ""
            print("Starting Event Stream...")
            try:
                for chunk in chain.stream(question):
                    text_chunk = ""
                    if isinstance(chunk, str):
                        text_chunk = chunk
                    elif hasattr(chunk, 'content'):
                        text_chunk = chunk.content
                    else:
                        text_chunk = str(chunk)
                    
                    full_answer += text_chunk
                    yield text_chunk
                
                print("Streaming complete. Full answer length:", len(full_answer))

                # Save Bot Message after completion
                if user.is_authenticated and chat_obj:
                     bot_msg = Chat_Message.objects.create(session_id=chat_obj, role='assistant', message=full_answer)
                     # Debug object to ensure it exists and has attributes
                     print(f"DTO keys: {bot_msg.__dict__.keys()}") 
                     print(f"Saved Bot Message: PK={bot_msg.pk}")

            except Exception as e:
                print("Error inside event_stream:")
                traceback.print_exc()
                yield f"Error: {str(e)}"

        response = StreamingHttpResponse(event_stream(), content_type='text/plain')
        if chat_obj:
            response['X-Chat-Session-Id'] = str(chat_obj.session_id)
        return response

    except Exception as e:
        print("=== Fatal Error in stream view ===")
        traceback.print_exc()
        return StreamingHttpResponse(f"Server Error: {str(e)}", status=500)

class ChatHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(username=self.request.user).order_by('-created_at')

class ChatMessageListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        # Ensure the session belongs to the user
        return Chat_Message.objects.filter(session_id__session_id=session_id, session_id__username=self.request.user).order_by('created_at')
