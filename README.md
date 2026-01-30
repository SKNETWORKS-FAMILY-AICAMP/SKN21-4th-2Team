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

---

# 💻 기술 스택 & 사용한 모델


| 분야                    | 사용 도구                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Language**            | [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white)](https://www.python.org/)                                                                                                                                                                                                                                                   |
| **Collaboration Tool**  | [![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/) [![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/) [![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/) |
| **LLM Model**           | [![GPT-4o](https://img.shields.io/badge/GPT--4o-mini%20-412991?style=for-the-badge&logo=openai&logoColor=white)](https://platform.openai.com/)                                                                                                                                                                                                                                     |
| **Embedding Model**     | [![text-embedding-3-small](https://img.shields.io/badge/text--embedding--3--small-00A67D?style=for-the-badge&logo=openai&logoColor=white)](https://platform.openai.com/docs/guides/embeddings)                                                                                                                                                                                     |
| **Vector DB**           | [![Pinecone](https://img.shields.io/badge/qdrant-0075A8?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech/)                                                                                                                                                                                                                                                    |
| **Orchestration / RAG** | [![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)                                                                                                                                                                                                                                       |
| **Development Env**     | [![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com/) [![Conda](https://img.shields.io/badge/Conda-3EB049?style=for-the-badge&logo=anaconda&logoColor=white)](https://www.anaconda.com/)                                                                                           |

<br>

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

---

# DB 스키마

![스키마](./assets/readme/erd-diagram.jpg)

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
| 이명준 |      |

