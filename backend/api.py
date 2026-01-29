# FastAPI 백엔드 서버
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# 프로젝트 루트 디렉토리를 sys.path에 추가
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from rag.config import Config
from rag.prompts.templates import get_persona_prompt, PERSONA_FILE_MAP
from rag.retriever.logic import operate_retriever
from rag.chain.pipeline import init_llm, create_chain
from langchain_core.runnables import RunnableLambda

# FastAPI 앱 생성
app = FastAPI(
    title="연애 상담 RAG API",
    description="페르소나 기반 연애 상담 챗봇 API",
    version="1.0.0"
)

# CORS 설정 (React 프론트엔드 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청/응답 모델 정의
class ChatRequest(BaseModel):
    question: str
    youtuber_name: str = "김달"  # 기본값: 김달

class ChatResponse(BaseModel):
    answer: str
    youtuber_name: str
    status: str = "success"

# 글로벌 변수로 LLM과 리트리버 캐싱
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


@app.get("/")
async def root():
    """서버 상태 확인"""
    return {
        "message": "연애 상담 RAG API 서버가 실행 중입니다.",
        "available_counselors": list(PERSONA_FILE_MAP.keys())
    }


@app.get("/api/counselors")
async def get_counselors():
    """사용 가능한 상담사 목록 반환"""
    counselors = [
        {"id": name, "name": name} 
        for name in PERSONA_FILE_MAP.keys() 
        if PERSONA_FILE_MAP[name] is not None
    ]
    return {"counselors": counselors}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    채팅 API - 선택된 상담사 페르소나로 응답 생성
    
    Args:
        request: ChatRequest (question, youtuber_name)
    
    Returns:
        ChatResponse (answer, youtuber_name, status)
    """
    try:
        # 1. 유튜버 이름 검증
        youtuber_name = request.youtuber_name
        if youtuber_name not in PERSONA_FILE_MAP:
            # 비슷한 이름 찾기 시도
            for name in PERSONA_FILE_MAP.keys():
                if youtuber_name in name or name in youtuber_name:
                    youtuber_name = name
                    break
            else:
                youtuber_name = "김달"  # 기본값
        
        if PERSONA_FILE_MAP.get(youtuber_name) is None:
            raise HTTPException(
                status_code=400, 
                detail=f"'{youtuber_name}' 상담사는 아직 준비되지 않았습니다."
            )
        
        # 2. LLM, 리트리버, 프롬프트 준비
        current_llm = get_llm()
        current_retriever = get_retriever()
        prompt = get_persona_prompt(youtuber_name=youtuber_name)
        
        # 3. 체인 생성 및 실행
        chain = create_chain(current_llm, current_retriever, prompt)
        response = chain.invoke(request.question)
        
        return ChatResponse(
            answer=response,
            youtuber_name=youtuber_name,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 채팅 처리 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"응답 생성 중 오류가 발생했습니다: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """서버 상태 및 설정 확인"""
    return {
        "status": "healthy",
        "model": Config.MODEL_NAME,
        "collection": Config.COLLECTION_NAME,
        "counselor_count": len([k for k, v in PERSONA_FILE_MAP.items() if v])
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("   연애 상담 RAG API 서버 시작")
    print("=" * 50)
    print(f"모델: {Config.MODEL_NAME}")
    print(f"상담사 수: {len([k for k, v in PERSONA_FILE_MAP.items() if v])}명")
    print("-" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
