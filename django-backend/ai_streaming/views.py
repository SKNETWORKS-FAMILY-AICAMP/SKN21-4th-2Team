from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid
import os
import sys
from pathlib import Path

# RAG 모듈 임포트
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from rag.prompts.templates import get_persona_prompt, PERSONA_FILE_MAP
from rag.retriever.logic import operate_retriever
from rag.chain.pipeline import init_llm, create_chain
from langchain_core.runnables import RunnableLambda

from .models import ChatSession, Message

# LLM 인스턴스 캐싱 (앱 시작 시 한 번만 초기화)
_llm_instance = None

def get_llm():
    """LLM 인스턴스를 캐싱하여 반환"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = init_llm()
    return _llm_instance


def index(request):
    """메인 채팅 페이지"""
    # 사용 가능한 페르소나 목록
    available_personas = [name for name, file in PERSONA_FILE_MAP.items() if file is not None]
    
    context = {
        'personas': available_personas,
    }
    return render(request, 'ai_streaming/chat.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def create_session(request):
    """새로운 채팅 세션 생성"""
    try:
        data = json.loads(request.body)
        persona = data.get('persona', '기본상담사')
        
        # 새 세션 생성
        session_id = str(uuid.uuid4())
        session = ChatSession.objects.create(
            session_id=session_id,
            persona=persona
        )
        
        # 초기 인사 메시지
        initial_message = Message.objects.create(
            session=session,
            role='assistant',
            content=f"안녕하세요, {persona}입니다. 어떤 고민이 있으신가요?"
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'message': initial_message.content
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def get_session_messages(request):
    """특정 세션의 모든 메시지 조회"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        session = get_object_or_404(ChatSession, session_id=session_id)
        messages = session.messages.all()
        
        messages_data = [
            {
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat()
            }
            for msg in messages
        ]
        
        return JsonResponse({
            'success': True,
            'messages': messages_data,
            'persona': session.persona
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
def chat_stream(request):
    """스트리밍 응답으로 AI 챗봇 답변 생성"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)
    
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        user_message = data.get('message')
        persona = data.get('persona', '기본상담사')
        
        # 세션 조회 또는 생성
        session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={'persona': persona}
        )
        
        # 사용자 메시지 저장
        Message.objects.create(
            session=session,
            role='user',
            content=user_message
        )
        
        def event_generator():
            """SSE(Server-Sent Events) 형식으로 스트리밍"""
            try:
                # RAG 체인 생성
                llm = get_llm()
                retriever = RunnableLambda(lambda q: operate_retriever(q, k=3) or [])
                prompt = get_persona_prompt(youtuber_name=persona)
                chain = create_chain(llm, retriever, prompt)
                
                # 스트리밍 응답 생성
                full_response = ""
                for chunk in chain.stream(user_message):
                    full_response += chunk
                    # SSE 형식으로 전송
                    yield f"data: {json.dumps({'token': chunk})}\n\n"
                
                # 완성된 응답 저장
                Message.objects.create(
                    session=session,
                    role='assistant',
                    content=full_response
                )
                
                # 완료 신호
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                error_msg = f"오류가 발생했습니다: {str(e)}"
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
        
        return StreamingHttpResponse(
            event_generator(),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            }
        )
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def change_persona(request):
    """페르소나 변경 및 대화 초기화"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        new_persona = data.get('persona')
        
        # 기존 세션 삭제 후 새로 생성
        ChatSession.objects.filter(session_id=session_id).delete()
        
        # 새 세션 생성
        session = ChatSession.objects.create(
            session_id=session_id,
            persona=new_persona
        )
        
        # 초기 메시지
        initial_message = Message.objects.create(
            session=session,
            role='assistant',
            content=f"안녕하세요, {new_persona}입니다. 어떤 고민이 있으신가요?"
        )
        
        return JsonResponse({
            'success': True,
            'message': initial_message.content
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)