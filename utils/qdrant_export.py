import json
from qdrant_client import QdrantClient

# 1. Qdrant 클라우드 연결
client = QdrantClient(
    url="https://7c78ac85-306b-4026-9bce-130101367b02.us-east4-0.gcp.cloud.qdrant.io", # 주신 주소
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.IS3oVvaD5GqKOd54ohQ4p9TVHKvG-tCfTicoO6FR-Mo"  # <-- 중요! 키가 있어야 접근 가능
)

# 2. 데이터 가져오기 (Scroll 기능 사용)
# limit는 한 번에 가져올 개수입니다. 데이터가 많으면 반복문으로 돌려야 합니다.
records, next_offset = client.scroll(
    collection_name="love_counseling_db",
    limit=1000,  # 일단 1000개만 가져와 봅니다.
    with_payload=True, # 텍스트 데이터(질문/답변)도 같이 가져옴
    with_vectors=False # 벡터(숫자 덩어리)는 필요 없으면 False (용량 절약)
)

# 3. JSON 파일로 저장
data_list = []
for record in records:
    data_list.append(record.payload) # payload 안에 실제 텍스트가 들어있습니다.

with open("export_data.json", "w", encoding="utf-8") as f:
    json.dump(data_list, f, ensure_ascii=False, indent=4)

print(f"총 {len(data_list)}개의 데이터를 저장했습니다!")