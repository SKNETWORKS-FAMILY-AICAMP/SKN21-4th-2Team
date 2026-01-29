# FastAPI 백엔드 서버
import os
import sys
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Header
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

# 데이터베이스 경로
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

# JWT 시크릿 키 (실제 운영에서는 환경변수로 관리)
SECRET_KEY = "your-secret-key-change-in-production"

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

# ============ 데이터베이스 초기화 ============
def init_db():
    """사용자 테이블 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ============ 인증 모델 ============
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ============ 인증 유틸리티 ============
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tokens (user_id, token, expires_at) VALUES (?, ?, ?)", 
                   (user_id, token, expires_at))
    conn.commit()
    conn.close()
    return token

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    token = authorization.split(" ")[1]
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.email FROM users u
        JOIN tokens t ON u.id = t.user_id
        WHERE t.token = ? AND t.expires_at > ?
    ''', (token, datetime.utcnow().isoformat()))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
    return {"id": user[0], "username": user[1], "email": user[2]}

# ============ 인증 API ============
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """회원가입 API"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (request.username, request.email, hash_password(request.password))
        )
        conn.commit()
        conn.close()
        return {"message": "회원가입 성공", "status": "success"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자명 또는 이메일입니다")

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """로그인 API"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?",
        (request.username, hash_password(request.password))
    )
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="사용자명 또는 비밀번호가 잘못되었습니다")
    token = create_token(user[0])
    return LoginResponse(
        access_token=token,
        user=UserResponse(id=user[0], username=user[1], email=user[2])
    )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(authorization: Optional[str] = Header(None)):
    """현재 로그인된 사용자 정보 조회"""
    user = get_current_user(authorization)
    return UserResponse(**user)

# ============ 기존 채팅 API ============
class ChatRequest(BaseModel):
    question: str
    youtuber_name: str = "김달"

class ChatResponse(BaseModel):
    answer: str
    youtuber_name: str
    status: str = "success"

llm = None
retriever = None

def get_llm():
    global llm
    if llm is None:
        llm = init_llm()
        print(f"✓ LLM 초기화 완료: {Config.MODEL_NAME}")
    return llm

def get_retriever():
    global retriever
    if retriever is None:
        retriever = RunnableLambda(lambda q: operate_retriever(q, k=5) or [])
        print("✓ 리트리버 초기화 완료")
    return retriever

@app.get("/")
async def root():
    return {
        "message": "연애 상담 RAG API 서버가 실행 중입니다.",
        "available_counselors": list(PERSONA_FILE_MAP.keys())
    }

@app.get("/api/counselors")
async def get_counselors():
    counselors = [
        {"id": name, "name": name} 
        for name in PERSONA_FILE_MAP.keys() 
        if PERSONA_FILE_MAP[name] is not None
    ]
    return {"counselors": counselors}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        youtuber_name = request.youtuber_name
        if youtuber_name not in PERSONA_FILE_MAP:
            for name in PERSONA_FILE_MAP.keys():
                if youtuber_name in name or name in youtuber_name:
                    youtuber_name = name
                    break
            else:
                youtuber_name = "김달"
        
        if PERSONA_FILE_MAP.get(youtuber_name) is None:
            raise HTTPException(status_code=400, detail=f"'{youtuber_name}' 상담사는 아직 준비되지 않았습니다.")
        
        current_llm = get_llm()
        current_retriever = get_retriever()
        prompt = get_persona_prompt(youtuber_name=youtuber_name)
        chain = create_chain(current_llm, current_retriever, prompt)
        response = chain.invoke(request.question)
        
        return ChatResponse(answer=response, youtuber_name=youtuber_name, status="success")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 채팅 처리 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"응답 생성 중 오류가 발생했습니다: {str(e)}")

@app.get("/api/health")
async def health_check():
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

