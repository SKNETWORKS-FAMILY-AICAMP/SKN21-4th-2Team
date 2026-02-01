# 시스템 구성도 - 명짝 (AI 연애 상담 챗봇)

---

## 시스템 아키텍처 개요

명짝 서비스는 3-tier 아키텍처를 기반으로, React 프론트엔드 → Django 백엔드 → RAG 파이프라인(Qdrant + OpenAI)으로 구성된다.

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| **Frontend** | React 18, Vite, CSS |
| **Backend** | Django 5.0, Django REST Framework |
| **Server** | Nginx (Reverse Proxy), Gunicorn (WSGI) |
| **LLM** | GPT-4o-mini (OpenAI) |
| **Embedding** | text-embedding-3-small (OpenAI) |
| **Vector DB** | Qdrant-Cloud|
| **RAG Framework** | LangChain |
| **Retrieval** | BM25 + Vector Similarity + MMR + Cross-Encoder Reranking |
| **Database** | SQLite (개발) / MySQL (운영, AWS RDS) |
| **Deployment** | AWS EC2 |

---

## 시스템 구성도

```
┌─────────────────────────────────────────────────────────────┐
│                        Client (Browser)                     │
│                    React SPA (Vite Build)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     AWS EC2 Instance                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 Nginx (Reverse Proxy)                  │  │
│  │         - Static Files (React Build) 서빙             │  │
│  │         - API 요청 → Gunicorn 프록시                  │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Gunicorn (WSGI Server)                    │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Django Backend (REST API)                 │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │  Account App │  │  Chat App   │  │  API Module  │  │  │
│  │  │  (인증/회원) │  │  (세션/메시지)│  │  (RAG 연동) │  │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘  │  │
│  │         │                │                 │          │  │
│  └─────────┼────────────────┼─────────────────┼──────────┘  │
│            │                │                 │              │
│            ▼                ▼                 ▼              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐│
│  │   SQLite /   │  │   SQLite /   │  │  RAG Pipeline      ││
│  │   MySQL DB   │  │   MySQL DB   │  │                    ││
│  │  (User,      │  │  (Chat,      │  │  Query Rewriting   ││
│  │   Session)   │  │   Message)   │  │       ↓            ││
│  └──────────────┘  └──────────────┘  │  Qdrant (Vector)   ││
│                                      │  + BM25 + MMR      ││
│                                      │       ↓            ││
│                                      │  Cross-Encoder     ││
│                                      │  Reranking         ││
│                                      │       ↓            ││
│                                      │  GPT-4o-mini       ││
│                                      │  + Persona Prompt  ││
│                                      └────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Qdrant  │ │  OpenAI  │ │  OpenAI  │
        │  Cloud   │ │  GPT-4o  │ │Embedding │
        │(VectorDB)│ │  -mini   │ │  API     │
        └──────────┘ └──────────┘ └──────────┘
```

---

## RAG 파이프라인 상세 구조

```
사용자 질문
    │
    ▼
[쿼리 리라이팅] ─── LLM이 검색 최적화 쿼리로 변환
    │
    ▼
[임베딩 생성] ─── text-embedding-3-small
    │
    ├──→ [벡터 유사도 검색] (Qdrant, 상위 40개)
    │         │
    │         ├──→ [MMR 검색] (12개, 관련성 + 다양성)
    │         │
    │         └──→ [BM25 검색] (12개, 키워드 매칭)
    │
    ▼
[하이브리드 병합] ─── 24개 후보 문서
    │
    ▼
[Cross-Encoder 리랭킹] ─── BAAI/bge-reranker-v2-m3
    │
    ▼
[최종 상위 3개 문서] ─── 컨텍스트로 사용
    │
    ▼
[LLM 응답 생성] ─── GPT-4o-mini + 시스템(BASE) 프롬프트 + 페르소나 프롬프트
    │
    ▼
[스트리밍 출력] ─── 사용자에게 실시간 응답
```

---

## 데이터베이스 구조

```
CustomUser (Django AbstractUser 확장)
    │ 1:N
    ▼
Chat (세션)
    - session_id (UUID, PK)
    - username (FK → CustomUser)
    - is_active (Boolean)
    - created_at / updated_at
    │ 1:N
    ▼
Chat_Message (메시지)
    - message_id (AutoField, PK)
    - session_id (FK → Chat)
    - role (user / assistant)
    - content (TextField)
    - created_at / updated_at

## 미구현
Persona (페르소나)
    - persona_id (AutoField, PK)
    - youtuber_name (CharField)
```

---

## API 엔드포인트(일부 구현)

### 인증
- `POST /account/create` - 회원가입
- `POST /account/login` - 로그인
- `POST /account/logout` - 로그아웃
- `GET /account/detail` - 프로필 조회
- `POST /account/update` - 정보 수정
- `POST /account/password_change` - 비밀번호 변경

### 채팅
- `POST /chat/chatting` - 메시지 전송 및 AI 응답
- `POST /api/chat/stream/` - 스트리밍 응답
- `GET /chat/chat_session` - 세션 조회
- `DELETE /chat/chat_session` - 세션 삭제

---

## 배포 구성

```
Internet → [Security Group (HTTP/HTTPS)]
               │
               ▼
          [AWS EC2 Instance]
           ├─ Nginx (Port 80/443)
           │   ├─ React 빌드 파일 서빙 (Static)
           │   └─ API 요청 → Gunicorn 프록시
           ├─ Gunicorn (Port 8000)
           │   └─ Django Application
           ├─ SQLite / MySQL (RDS)
           └─ Python 가상환경 (.venv)
```
