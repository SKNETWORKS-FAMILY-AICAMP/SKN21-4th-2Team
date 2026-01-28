import json
from django.shortcuts import render
from django.http import JsonResponse
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
    Handle chat requests.
    Expects JSON data with 'question' and 'youtuber'.
    """
    try:
        data = json.loads(request.body)
        question = data.get('question')
        youtuber_name = data.get('youtuber')

        if not question or not youtuber_name:
            return JsonResponse({'error': 'Missing question or youtuber selection'}, status=400)

        # Initialize RAG components
        # Note: In a production app, LLM initialization might be cached or done globally
        llm = init_llm()
        
        # Retriever
        # We wrap the operate_retriever in a RunnableLambda as per main.py usage
        retriever = RunnableLambda(lambda q: operate_retriever(q, k=5) or [])
        
        # Prompt
        prompt = get_persona_prompt(youtuber_name=youtuber_name)
        
        # Chain
        chain = create_chain(llm, retriever, prompt)
        
        # Invoke
        response = chain.invoke(question)
        
        return JsonResponse({'answer': response})

    except Exception as e:
        print(f"Error processing chat request: {e}")
        return JsonResponse({'error': str(e)}, status=500)
