import json
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from langchain_core.runnables import RunnableLambda

from rag.config import Config
from rag.chain.pipeline import init_llm, create_chain
from rag.prompts.templates import get_persona_prompt, PERSONA_FILE_MAP
from rag.retriever.logic import operate_retriever

@ensure_csrf_cookie
def index(request):
    """
    Render the main chat interface.
    Pass the list of available personas (Youtubers) to the template.
    """
    youtubers = list(PERSONA_FILE_MAP.keys())
    return render(request, 'index.html', {'youtubers': youtubers})

@require_http_methods(["POST"])
def chat(request):
    """
    Handle chat requests with streaming response.
    Expects JSON data with 'question' and 'youtuber'.
    """
    try:
        data = json.loads(request.body)
        question = data.get('question')
        youtuber_name = data.get('youtuber')

        if not question or not youtuber_name:
            return JsonResponse({'error': 'Missing question or youtuber selection'}, status=400)

        # Initialize RAG components
        llm = init_llm()
        
        # Retriever
        retriever = RunnableLambda(lambda q: operate_retriever(q, k=5) or [])
        
        # Prompt
        prompt = get_persona_prompt(youtuber_name=youtuber_name)
        
        # Chain
        chain = create_chain(llm, retriever, prompt)
        
        # Generator for streaming
        def stream_generator():
            try:
                for chunk in chain.stream(question):
                    # 만약 chunk가 문자열이 아니면 문자열로 변환
                    content = str(chunk)
                    if content:
                        yield content
            except Exception as e:
                # 스트리밍 도중 에러 발생 시 처리 (클라이언트에 에러 텍스트 전송)
                yield f"[Error generating response: {str(e)}]"

        return StreamingHttpResponse(stream_generator(), content_type='text/plain')

    except Exception as e:
        print(f"Error processing chat request: {e}")
        return JsonResponse({'error': str(e)}, status=500)
