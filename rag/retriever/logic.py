import os
import sys

# 프로젝트 루트 디렉토리를 sys.path에 추가하여 모듈 인식 문제 해결
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from rag.config import Config
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import os
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from dotenv import load_dotenv
load_dotenv()

QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

COLLECTION_NAME = "love_counseling_db"
reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")

def rewrite_query(original_query):
    """
    사용자의 질문을 검색에 최적화된 형태로 재작성합니다.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
    
    # 📝 연애 상담 데이터셋의 특성에 맞춘 프롬프트 설정
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 질문 재작성 전문가입니다. 사용자의 질문을 검색 엔진이 연애 상담 사례 데이터베이스에서 가장 유사한 사례를 잘 찾을 수 있도록 더 구체적이고 명확한 문장으로 한 줄만 재작성하세요."),
        ("human", f"원래 질문: {original_query}")
    ])
    
    chain = prompt | llm
    rewritten_query = chain.invoke({}).content
    print(f"🔄 재작성된 질문: {rewritten_query}") # 디버깅용
    return rewritten_query


def bm25_search(query, corpus_docs, k=3):
    tokenized = [d.page_content.split() for d in corpus_docs]
    bm25 = BM25Okapi(tokenized)

    scores = bm25.get_scores(query.split())
    topk_idx = np.argsort(scores)[::-1][:k]

    return [corpus_docs[i] for i in topk_idx]


def mmr(query_vec, doc_vecs, docs, k, lambda_mult=0.5):
    selected = []
    selected_idx = []

    sim_to_query = cosine_similarity([query_vec], doc_vecs)[0]
    sim_between_docs = cosine_similarity(doc_vecs)

    for _ in range(k):
        if len(selected_idx) == 0:
            idx = int(np.argmax(sim_to_query))
        else:
            remaining = list(set(range(len(docs))) - set(selected_idx))
            mmr_scores = []

            for i in remaining:
                diversity = max(sim_between_docs[i][j] for j in selected_idx)
                score = lambda_mult * sim_to_query[i] - (1 - lambda_mult) * diversity
                mmr_scores.append((score, i))

            idx = max(mmr_scores)[1]

        selected_idx.append(idx)
        selected.append(docs[idx])

    return selected


def rerank(query, docs, top_n=3):
    pairs = [[query, d.page_content] for d in docs]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
    return [d for _, d in ranked[:top_n]]

def build_text_from_payload(payload: dict) -> str:
    content = payload.get("content", {})

    parts = []

    if "situation_summary" in content:
        parts.append(f"상황: {content['situation_summary']}")

    if "core_conflict" in content:
        parts.append(f"갈등: {content['core_conflict']}")

    if "key_advice" in content:
        parts.append("핵심 조언: " + " ".join(content["key_advice"]))

    if "do" in content:
        parts.append("권장 행동: " + " ".join(content["do"]))

    if "dont" in content:
        parts.append("피해야 할 행동: " + " ".join(content["dont"]))

    return "\n".join(parts)

def pretty_print_docs(docs):
    print("\n====== Retrieval Results ======\n")

    for i, d in enumerate(docs, 1):
        print(f"[{i}] --------------------------")

        meta = d.metadata.get("retrieval", {})
        context = d.metadata.get("context", {})

        print("주제:", meta.get("main_topic"))
        print("단계:", meta.get("relationship_stage"))
        print("감정:", meta.get("emotion"))

        print("위험도:", context.get("risk_level"))
        print("스타일:", context.get("advisor_style"))

        print("\nSummary:")
        print(d.page_content[:400], "...\n")


# def operate_retriever(query_text, k=3):
#     print(f"--- 🔍 질문: '{query_text}' ---")

#     try:
#         client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
#         embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)
#         query_vector = np.array(embeddings.embed_query(query_text))

#         resp = client.query_points(
#             collection_name=COLLECTION_NAME,
#             query=query_vector.tolist(),
#             limit=40,
#             with_payload=True,
#             with_vectors=True,
#         )

#         docs = []
#         vectors = []
#         for p in resp.points:
#             payload = p.payload or {}
#             text = build_text_from_payload(payload)
#             if not text.strip():
#                 continue

#             docs.append(Document(page_content=text,
#                     metadata={"retrieval": payload.get("retrieval"),
#                               "context": payload.get("context"),"id": p.id,"score": p.score}))
#             vectors.append(p.vector)

#         if len(docs) == 0:
#             print("Qdrant에서 텍스트 payload를 찾지 못함.")
#             return []

#         mmr_docs = mmr(query_vector, np.array(vectors), docs, k=12)

#         bm25_docs = bm25_search(query_text, docs, k=12)
#         hybrid_docs = mmr_docs + bm25_docs

#         pairs = [[query_text, d.page_content] for d in hybrid_docs]
#         scores = reranker.predict(pairs)

#         ranked = sorted(zip(scores, hybrid_docs), key=lambda x: x[0], reverse=True)
#         final_docs = [d for _, d in ranked[:k]]
#         return final_docs



#     except Exception as e:
#         print(f"Error: {e}")
#         return None


# if __name__ == "__main__":
#     query = "첫사랑이 계속 생각나서 새로운 사람을 못 만나겠어요"
#     docs = operate_retriever(query, k=3)
#     pretty_print_docs(docs)
def operate_retriever(query_text, k=3):
    print(f"--- 🔍 원래 질문: '{query_text}' ---")

    try:
        # 환경 변수 확인
        if not QDRANT_URL:
            raise ValueError("QDRANT_URL 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
        if not QDRANT_API_KEY:
            raise ValueError("QDRANT_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
        
        # 🚀 1. Query Rewriting 적용 (검색용 쿼리 생성)
        search_query = rewrite_query(query_text)

        # Qdrant 클라이언트 생성 (연결 오류 처리)
        try:
            client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        except Exception as conn_error:
            error_msg = f"Qdrant 서버 연결 실패: {conn_error}\n"
            error_msg += f"QDRANT_URL: {QDRANT_URL}\n"
            error_msg += "확인사항:\n"
            error_msg += "1. Qdrant 서버가 실행 중인지 확인하세요\n"
            error_msg += "2. QDRANT_URL이 올바른지 확인하세요 (예: http://localhost:6333 또는 클라우드 URL)\n"
            error_msg += "3. 방화벽이 연결을 차단하지 않는지 확인하세요"
            raise ConnectionError(error_msg) from conn_error
        
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)
        
        # 🚀 2. 재작성된 쿼리로 벡터 생성
        query_vector = np.array(embeddings.embed_query(search_query))

        resp = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector.tolist(),
            limit=40,
            with_payload=True,
            with_vectors=True,
        )

        docs = []
        vectors = []
        for p in resp.points:
            payload = p.payload or {}
            text = build_text_from_payload(payload)
            if not text.strip():
                continue

            docs.append(Document(page_content=text,
                    metadata={"retrieval": payload.get("retrieval"),
                              "context": payload.get("context"),"id": p.id,"score": p.score}))
            vectors.append(p.vector)

        if len(docs) == 0:
            print("Qdrant에서 텍스트 payload를 찾지 못함.")
            return []

        # 🚀 3. MMR 검색 (재작성된 벡터 사용)
        mmr_docs = mmr(query_vector, np.array(vectors), docs, k=12)

        # 🚀 4. BM25 검색 (재작성된 텍스트 쿼리 사용)
        bm25_docs = bm25_search(search_query, docs, k=12)
        hybrid_docs = mmr_docs + bm25_docs

        # 🚀 5. Rerank (최종 랭킹은 원래 질문(query_text)과 비교하는 것이 의도 파악에 더 유리할 수 있음)
        pairs = [[search_query, d.page_content] for d in hybrid_docs]
        scores = reranker.predict(pairs)

        ranked = sorted(zip(scores, hybrid_docs), key=lambda x: x[0], reverse=True)
        final_docs = [d for _, d in ranked[:k]]
        return final_docs

    except ConnectionError as e:
        print(f"❌ 연결 오류: {e}")
        return []
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
        return []
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return []


# def get_retriever(vector_store, search_type="similarity", k=4):
#     """
#     팀원 3이 구현할 검색 로직 (유사도 검색, MMR 등)
#     """




# def run_retriever_example(query_text, k=3):
#     """
#     Retriever 베이스 로직
#     """
#     print(f"--- 🔍 질문: '{query_text}' ---")

#     try:
#         # 1. Qdrant / Embedding 객체 생성
#         client = QdrantClient(
#             url=Config.QDRANT_URL,
#             api_key=Config.QDRANT_API_KEY
#         )

#         embeddings = OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             openai_api_key=Config.OPENAI_API_KEY
#         )

#         # 2. 질문 → 벡터
#         query_vector = embeddings.embed_query(query_text)

#         # 3. 벡터 유사도 검색
#         response = client.query_points(
#             collection_name=Config.COLLECTION_NAME,
#             query=query_vector,
#             limit=k,
#             with_payload=True
#         )

#         return response  # QueryResponse 반환

#     except Exception as e:
#         print(f"🔥 에러 발생: {e}")
#         return None

# def print_retriever_results(query_text, k=3):
#     """
#     Retriever 결과를 상세하게 터미널에 출력하는 함수
#     Args:
#         query_text: 질문 텍스트
#         k: 검색 결과 개수
#     """
#     # run_retriever_example로 검색 수행
#     response = run_retriever_example(query_text, k=k)
    
#     if not response or not response.points:
#         print("❌ 검색 결과가 없습니다.")
#         return
    
#     print(f"\n✅ 총 {len(response.points)}개의 관련 문서를 찾았습니다.\n")
#     print("=" * 80)
    
#     for i, point in enumerate(response.points, 1):
#         payload = point.payload or {}
#         content_box = payload.get("content", {})
        
#         # 문서 정보 추출
#         situation = content_box.get("situation_summary", "내용 없음")
#         advice = content_box.get("key_advice", [])
        
#         # advice 리스트를 문자열로 변환
#         if isinstance(advice, list):
#             advice_str = "\n   • ".join(advice) if advice else "조언 없음"
#         else:
#             advice_str = str(advice)
        
#         # 결과 출력
#         print(f"\n📄 문서 #{i} (유사도 점수: {point.score:.4f})")
#         print("-" * 80)
#         print(f"📌 상황 요약:")
#         print(f"   {situation}")
#         print(f"\n💡 핵심 조언:")
#         print(f"   • {advice_str}")
        
#         # 추가 메타데이터가 있다면 출력
#         if payload.get("metadata"):
#             print(f"\n📊 추가 정보: {payload.get('metadata')}")
        
#         # 디버깅용 - content_box가 비어있으면 전체 payload 출력
#         if not content_box:
#             print(f"\n⚠️ [디버깅] 전체 Payload: {payload}")
        
#         print("=" * 80)
    
#     print()
#     return response





