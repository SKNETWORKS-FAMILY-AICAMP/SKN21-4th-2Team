# 🖐️ 팀 소개

- ## 팀명 : **명짝**
- ### 팀원 소개 :

<div align="center">
	
| [김승룡] | [정덕규] | [이의정] | [진승언] | [이명준] |
| :---: | :---: | :---: | :---: | :---: |
| <img src="https://loremflickr.com/200/200/dog?lock=1" width="120" alt="dog1"> | <img src="https://loremflickr.com/200/200/dog?lock=20" width="120" alt="dog2"> | <img src="https://loremflickr.com/200/200/dog?lock=30" width="120" alt="dog3"> | <img src="https://loremflickr.com/200/200/dog?lock=4" width="120" alt="dog4"> | <img src="https://loremflickr.com/200/200/dog?lock=5" width="120" alt="dog5"> |
</div>
<br>

- ### 팀원 역할:

  ```markdown
  - 백엔드 (Django build, Django View, Django → Session ) - 덕규
  - 데브옵스(Docker, AWS EC2, Amazon RDS, Nginx) - 승언
  - 프론트( Javascript, React) - 의정
  - AI 에이전트 (django  method 비동기 스트리밍, RAG기반 챗봇 성능개선) - 명준
  - DBA (qdrant, Django model) - 승룡
  ```

---

# 📖 프로젝트 개요

## 주제 : 모두가 관심있어하는, 인류 생존에 가장 중요한 연애! <br> 어떻게 하면 더 나은 연애를 할 수 있을지 상담해주는 AI 기반의 '연애 상담' 챗봇 서비스

- ### **프로젝트 소개**

"**명짝 : 명준(님) 짝꿍구하기**"는 사용자의 연애에 대한 고민을 상담해주는 AI 대화형 챗봇 서비스입니다.**연애를 하면서 생기는 다양한 상황과 질문에 대한 답변를 RAG 기반으로 안내**하며**사용자가 선호하는 연애 유튜버의 말투로 답변**합니다.

- ### **프로젝트 배경**

"연애를 하다보면, 또는 연애를 시작하려고 하면<br>
남들에게 물어보기도 어려운 다양한 상황에 직면하게 됩니다.<br>
이럴 때 저희 AI 챗봇에 물어보면 됩니다.."<br>

## 본 프로젝트가 필요한 이유

### 연애 고민은 혼자 감당하기엔 너무 크다

- 사소해 보여도 감정·자존감·판단력을 흔들며, 주변에 말하기도 어렵다.

### 감정 때문에 생각이 왜곡된다

- 불안, 자기비난, 과한 해석 속에서 스스로 객관화가 힘들다.

### 사람 상담의 한계를 보완한다

- 지인 상담의 편향, 전문가 상담의 비용·접근성 문제를 해결한다.

### 결정 직전 타이밍을 잡아준다

- 연락·답장·이별 같은 순간에 감정 폭주를 막아준다.

### 정답 없는 연애를 구조화해준다

- 상황 분석 → 선택지 → 결과 예측까지 정리해준다.

### 반복되는 연애 패턴을 인식하게 한다

- 기록과 정리를 통해 ‘왜 힘든지’를 언어화하게 돕는다.

<br>



## 💻 기술 스택 & 사용한 모델

| 분야 | 사용 도구 |
| :--- | :--- |
| **Language** | ![Python](https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) |
| **Frontend** | ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white) |
| **Backend** | ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white) |
| **Infrastructure** | ![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) |
| **Collaboration Tool** | ![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) |
| **Vector DB** | ![Qdrant](https://img.shields.io/badge/qdrant-%23bd1c2b.svg?style=for-the-badge&logo=qdrant&logoColor=white) |
| **Orchestration** | ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white) |


## 📊 데이터 구축 및 검색 프로세스 (Data Processing & RAG Flow)

### 1. 데이터 수집 및 전처리 자동화 (Data Pipeline)
기존의 수동 스크립트 복사 방식의 비효율성을 개선하기 위해 **`youtube_transcript_api`**를 활용한 **End-to-End 데이터 파이프라인**을 자체 구축하였습니다.

- **자동화 로직:** YouTube URL 입력 ➔ 자막(Script) 자동 추출 ➔ 텍스트 정제 ➔ CSV 변환 ➔ Vector DB 적재
- **전처리 (Pre-processing):**
  - 영상 데이터 특유의 **불용어(추임새, 반복어)** 제거 및 구어체 정규화 수행
  - 텍스트 길이에 따른 청크(Chunk) 분할 및 임베딩 변환
- **성과:** 데이터 구축 시간을 획기적으로 단축하고, LLM 학습에 최적화된 고품질 데이터셋 확보

### 2. Qdrant Vector DB 구조 (Schema & Payload)
수집된 상담 데이터는 **Qdrant**에 벡터(Vector)와 메타데이터(Payload) 형태로 구조화되어 저장됩니다. 단순 텍스트 매칭이 아닌, 의미 기반 검색을 위해 Payload를 상세하게 설계했습니다.

| 필드명 (Key) | 설명 (Description) | 예시 (Example) |
| :--- | :--- | :--- |
| **id** | 고유 벡터 ID | `5f3a...` |
| **vector** | OpenAI Embedding Vector | `[0.012, -0.034, ...]` (1536 dim) |
| **payload.page_content** | 실제 상담 대화 내용 | "권태기가 왔을 때는..." |
| **payload.source** | 원본 유튜브 영상 URL | `https://youtu.be/...` |
| **payload.title** | 영상 제목 | "연애의 참견 3회" |
| **payload.speaker** | 화자 정보 | "상담가 A" |

### 3. 검색 및 답변 생성 원리 (Retrieval & Display)
사용자가 질문을 입력하면 시스템은 다음과 같은 흐름으로 최적의 답변을 생성하여 화면에 표시합니다.

1.  **Query Embedding:** 사용자의 질문(Input)을 임베딩 모델을 통해 벡터로 변환합니다.
2.  **Semantic Search:** Qdrant DB에서 질문 벡터와 가장 유사도(Cosine Similarity)가 높은 Top-k개의 상담 로그를 검색합니다.
3.  **Context Injection:** 검색된 상담 내용(`page_content`)과 메타데이터(`source`)를 프롬프트에 포함하여 LLM에 전달합니다.
4.  **Response Generation:** LLM은 상담 데이터를 근거로 페르소나에 맞는 위로와 조언을 생성합니다.
5.  **Frontend Display:**
    - **채팅:** 생성된 답변을 말풍선 형태로 출력
    - **참거 출처:** Payload에 저장된 `source` URL을 활용하여, 답변의 근거가 된 **YouTube 영상 링크**를 함께 제공

---

# 🪢시스템 아키텍처

### 프로젝트 구조****

```markdown
    프론트엔드:
        웹 프레임워크: React 
    백엔드/ AI: 
        프록시: NGINX 
        웹 프레임워크: Django(전통적인 API, 애플리케이션 데이터설계)
        웹 통신 게이트웨이: WSGI
        AI 통신 방식: Django.StreamingHttpResponse 
        RESTFUL api: Django
    배포: 
        Web Server: EC-2 
        RDB: Amazon RDS 
        VectorDB: qdrantcloud
```

### 백엔드 구조도

![백엔드](assets/readme/client2django-app.jpg)

### 시스템 아키텍처 구조도

![시스템구조도](assets/readme/system-diagram.jpg)

---

# DB 스키마

![스키마](assets/readme/erd-diagram.jpg)

<br>

---

---

# 🐛 트러블슈팅

<br>

---

# 🤖 데모(시연 페이지)


---

# ✒️ 한 줄 회고


| 이름   | 회고 |
| -------- | ------ |
| 김승룡 |      |
| 정덕규 |      |
| 이의정 |      |
| 진승언 |      |
| 이명준 |  개발자가 반드시 이해해야하는 `설계 - 개발 - 테스트 - 배포`의 전체 흐름을 느낄 수 있어 좋았습니다.   |

