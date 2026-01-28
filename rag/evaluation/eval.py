import os
import pandas as pd
from dotenv import load_dotenv
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import answer_relevancy

from langchain_openai import ChatOpenAI

# ===============================
# 환경 변수 로드
# ===============================
load_dotenv()


# ===============================
# 평가 실행 함수
# ===============================
def run_evaluation():
    test_questions = [
        "여자친구와 연락 문제로 자주 싸워. 내가 너무 집착하는 걸까?",
        "썸 타는 사람이 카톡 답장이 너무 느려. 이거 그린라이트 맞아?",
    ]

    results = {
        "question": [],
        "answer_no_prompt": [],
        "answer_with_prompt": [],
        "relevancy_no_prompt": [],
        "relevancy_with_prompt": [],
    }

    # Chat LLM (invoke 방식 사용)
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    for q in test_questions:
        print(f"\n📝 질문 처리 중: {q}")

        # ======================================
        # 1. Prompt / RAG 없이 답변 생성
        # ======================================
        try:
            response = llm.invoke(q)
            answer_no_prompt = response.content
            print(f"🔹 Answer without prompt:\n{answer_no_prompt}")
        except Exception as e:
            print(f"❌ Error generating answer without prompt: {e}")
            answer_no_prompt = ""

        # ======================================
        # 2. Prompt + RAG 기반 답변 생성
        # ======================================
        try:
            from retrieve_test import get_rag_response

            rag_response = get_rag_response(q, prompt_file="prompt.md")
            answer_with_prompt = rag_response.get("answer", "")
            print(f"🔹 Answer with prompt:\n{answer_with_prompt}")
        except Exception as e:
            print(f"❌ Error generating answer with prompt: {e}")
            answer_with_prompt = ""

        # ======================================
        # 3. Ragas answer_relevancy 평가
        # ======================================
        try:
            dataset_no_prompt = Dataset.from_dict(
                {
                    "question": [q],
                    "answer": [answer_no_prompt],
                }
            )

            score_no_prompt = evaluate(
                dataset=dataset_no_prompt, metrics=[answer_relevancy], llm=llm
            )

            relevancy_no_prompt = score_no_prompt["answer_relevancy"]
        except Exception as e:
            print(f"❌ Error calculating relevancy (no prompt): {e}")
            relevancy_no_prompt = None

        try:
            dataset_with_prompt = Dataset.from_dict(
                {
                    "question": [q],
                    "answer": [answer_with_prompt],
                }
            )

            score_with_prompt = evaluate(
                dataset=dataset_with_prompt, metrics=[answer_relevancy], llm=llm
            )

            relevancy_with_prompt = score_with_prompt["answer_relevancy"]
        except Exception as e:
            print(f"❌ Error calculating relevancy (with prompt): {e}")
            relevancy_with_prompt = None

        # ======================================
        # 4. 결과 저장
        # ======================================
        results["question"].append(q)
        results["answer_no_prompt"].append(answer_no_prompt)
        results["answer_with_prompt"].append(answer_with_prompt)
        results["relevancy_no_prompt"].append(relevancy_no_prompt)
        results["relevancy_with_prompt"].append(relevancy_with_prompt)

    # ======================================
    # 결과 파일 저장
    # ======================================
    df = pd.DataFrame(results)
    output_file = "answer_relevancy_comparison.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"\n💾 평가 결과가 '{output_file}' 파일로 저장되었습니다.")


if __name__ == "__main__":
    run_evaluation()
