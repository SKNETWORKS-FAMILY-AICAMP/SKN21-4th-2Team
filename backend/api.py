# RAG 핵심 로직 (Django에서 재사용)
import os
import sys

# 프로젝트 루트 디렉토리를 sys.path에 추가
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from rag.config import Config
from rag.prompts.templates import get_persona_prompt, PERSONA_FILE_MAP
from rag.retriever.logic import operate_retriever
from rag.chain.pipeline import init_llm, create_chain
from langchain_core.runnables import RunnableLambda

# ============ 싱글톤 인스턴스 ============
llm = None
retriever = None

def get_llm():
    """LLM 인스턴스를 반환 (싱글톤 패턴)"""
    global llm
    if llm is None:
        llm = init_llm()
        print(f"✓ LLM 초기화 완료: {Config.MODEL_NAME}")
    return llm

def get_retriever():
    """리트리버 인스턴스를 반환 (싱글톤 패턴)"""
    global retriever
    if retriever is None:
        retriever = RunnableLambda(lambda q: operate_retriever(q, k=5) or [])
        print("✓ 리트리버 초기화 완료")
    return retriever

def get_available_counselors():
    """사용 가능한 상담사 목록 반환"""
    return [
        {"id": name, "name": name} 
        for name in PERSONA_FILE_MAP.keys() 
        if PERSONA_FILE_MAP[name] is not None
    ]

def process_chat(question: str, youtuber_name: str = "김달") -> dict:
    """
    채팅 처리 핵심 로직
    
    Args:
        question: 사용자 질문
        youtuber_name: 상담사 이름 (기본값: 김달)
    
    Returns:
        dict: {"answer": str, "youtuber_name": str, "status": str}
    """
    try:
        # 상담사 이름 매칭
        if youtuber_name not in PERSONA_FILE_MAP:
            for name in PERSONA_FILE_MAP.keys():
                if youtuber_name in name or name in youtuber_name:
                    youtuber_name = name
                    break
            else:
                youtuber_name = "김달"
        
        # 상담사 유효성 검사
        if PERSONA_FILE_MAP.get(youtuber_name) is None:
            return {
                "answer": f"'{youtuber_name}' 상담사는 아직 준비되지 않았습니다.",
                "youtuber_name": youtuber_name,
                "status": "error"
            }
        
        # RAG 체인 실행
        current_llm = get_llm()
        current_retriever = get_retriever()
        prompt = get_persona_prompt(youtuber_name=youtuber_name)
        chain = create_chain(current_llm, current_retriever, prompt)
        response = chain.invoke(question)
        
        return {
            "answer": response,
            "youtuber_name": youtuber_name,
            "status": "success"
        }
    except Exception as e:
        print(f"❌ 채팅 처리 중 오류: {e}")
        return {
            "answer": f"응답 생성 중 오류가 발생했습니다: {str(e)}",
            "youtuber_name": youtuber_name,
            "status": "error"
        }

def get_health_status() -> dict:
    """서버 상태 정보 반환"""
    return {
        "status": "healthy",
        "model": Config.MODEL_NAME,
        "collection": Config.COLLECTION_NAME,
        "counselor_count": len([k for k, v in PERSONA_FILE_MAP.items() if v])
    }
