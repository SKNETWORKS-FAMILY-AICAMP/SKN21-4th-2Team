
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse 

from .models import Chat, Chat_Message
from .serializers import PostSerializer
from rest_framework import generics
from rest_framework.decorators import api_view
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

# Create your views here.

def index(request):
    return render(request, 'chat/index.html')

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