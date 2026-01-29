## streamlit app
import streamlit as st
import os
import itertools
import time
import base64
from dotenv import load_dotenv

# RAG 관련 모듈 임포트
from rag.config import Config
from rag.prompts.templates import get_persona_prompt, PERSONA_FILE_MAP
from rag.retriever.logic import operate_retriever
from rag.chain.pipeline import init_llm, create_chain
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage

# 1. 환경 변수 로드
load_dotenv()

# 2. 페이지 설정
st.set_page_config(page_title="RAG 연애 상담소", page_icon="❤️", layout="wide")

# 🚀 속도 개선: 이미지 캐싱
@st.cache_data
def get_image_base64(path):
    if not os.path.exists(path): return ""
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 🚀 LLM 및 Retriever 관련 캐싱
@st.cache_resource
def get_llm():
    return init_llm()

# Retriever는 매번 생성하지 않고, 로직 함수 자체를 활용하므로 별도 캐싱 불필요하거나 단순 래핑
def get_rag_chain(persona_name):
    llm = get_llm()
    # main.py와 동일한 retriever 설정
    retriever = RunnableLambda(lambda q: operate_retriever(q, k=3) or [])
    prompt = get_persona_prompt(youtuber_name=persona_name)
    chain = create_chain(llm, retriever, prompt)
    return chain

# 🎨 CSS 설정
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F5F2F2; }}
    h1, h2, h3 {{ color: #333333 !important; text-align: center; }}
    
    /* 아바타 숨기기 */
    [data-testid="stChatMessageAvatarAssistant"], 
    [data-testid="stChatMessageAvatarUser"] {{ 
        display: none !important; 
    }}
    
    /* 모든 채팅 메시지 기본 스타일 */
    [data-testid="stChatMessage"] {{
        border-radius: 20px; 
        padding: 10px 15px; 
        margin-bottom: 20px; 
        display: flex !important;
    }}

    /* 👤 사용자 대화창 */
    .stChatMessage[aria-label="user"] {{
        background-color: #5A7ACD !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        flex-direction: row-reverse !important;
        width: fit-content !important;
        max-width: 80% !important;
    }}
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
        background-color: #5A7ACD !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        flex-direction: row-reverse !important;
        width: fit-content !important;
        max-width: 80% !important;
    }}

    /* 사용자 창 내부 텍스트 스타일 */
    .stChatMessage[aria-label="user"] .stMarkdown p,
    .stChatMessage[aria-label="user"] p,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {{
        color: #FFFFFF !important;
        text-align: right !important;
        font-weight: 500 !important;
    }}

    /* 🤖 상담사 대화창 */
    .stChatMessage[aria-label="assistant"],
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
        background-color: #FFC50F !important;
        margin-right: auto !important;
        margin-left: 0 !important;
        width: 100% !important;
    }}
    
    .stChatMessage[aria-label="assistant"] .stMarkdown p,
    .stChatMessage[aria-label="assistant"] p,
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p {{
        color: #333333 !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }}

    img {{ border-radius: 0px !important; }}

    .intro-overlay {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #F5F2F2; display: flex; flex-direction: column;
        align-items: center; justify-content: center; z-index: 999999;
    }}
    </style>
    """, unsafe_allow_html=True)

# ✨ 3. 인트로 애니메이션
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    intro_placeholder = st.empty()
    welcome_text = "당신의 연애 고민, 우리가 들어줄게요 ❤️"
    img_files = ["assets/heart_o.png", "assets/heart_a.png", "assets/heart_closed.png"]
    # 이미지가 존재하지 않을 경우를 대비해 예외처리
    try:
        img_data = [get_image_base64(f) for f in img_files]
        if all(img_data):
            mouth_cycle = itertools.cycle(img_data)
            typed_text = ""
            for char in welcome_text:
                typed_text += char
                with intro_placeholder.container():
                    st.markdown(f'<div class="intro-overlay"><img src="data:image/png;base64,{next(mouth_cycle)}" style="width:350px;"><div style="background:#F5F2F2; padding:20px; border-radius:40px; color:#333333; font-size:26px; font-weight:bold; box-shadow:0 10px 25px rgba(0,0,0,0.3);">{typed_text}</div></div>', unsafe_allow_html=True)
                time.sleep(0.08)
    except Exception:
        pass # 이미지가 없으면 애니메이션 스킵
        
    st.session_state.intro_done = True
    st.rerun()

# --- 사이드바: 유튜버 페르소나 선택 ---
st.sidebar.title("상담사 선택")
available_youtubers = [name for name, file in PERSONA_FILE_MAP.items() if file is not None]
selected_persona = st.sidebar.selectbox(
    "원하는 상담 스타일을 선택하세요:",
    available_youtubers,
    index=0 if available_youtubers else 0
)

# 페르소나 변경 감지 및 대화 초기화
if "current_persona" not in st.session_state:
    st.session_state.current_persona = selected_persona

if st.session_state.current_persona != selected_persona:
    st.session_state.current_persona = selected_persona
    st.session_state.messages = [{"role": "assistant", "content": f"안녕하세요, {selected_persona}입니다. 어떤 고민이 있으신가요?"}]
    st.rerun()

# --- 4. 본 화면 ---
st.markdown(f"<h1 style='color: #333333 !important;'>❤️ {selected_persona}의 연애 상담소 ❤️</h1>", unsafe_allow_html=True)
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"안녕하세요, {selected_persona}입니다. 어떤 고민이 있으신가요?"}]

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            col1, col2 = st.columns([1, 4])
            with col1: 
                # 상담사 이미지는 공통으로 사용 (필요시 페르소나별 이미지 분기 가능)
                if os.path.exists("assets/heart_closed.png"):
                    st.image("assets/heart_closed.png", width=120)
                else:
                    st.write("🤖")
            with col2: st.markdown(f"<p>{message['content']}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p>{message['content']}</p>", unsafe_allow_html=True)

# 사용자 입력 처리
if prompt := st.chat_input("고민을 털어놓으세요..."):
    # 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<p>{prompt}</p>", unsafe_allow_html=True)

    # 답변 생성 및 표시
    with st.chat_message("assistant"):
        col_char, col_txt = st.columns([1, 4])
        
        with col_char: 
            char_container = st.empty()
            if os.path.exists("assets/heart_closed.png"):
                char_container.image("assets/heart_closed.png", width=120)
            else:
                char_container.write("🤖")
                
        with col_txt: 
            msg_container = st.empty()
        
        full_response = ""
        
        # 이미지 애니메이션 준비
        chat_mouth_cycle = None
        img_files = ["assets/heart_o.png", "assets/heart_a.png", "assets/heart_closed.png"]
        if all(os.path.exists(f) for f in img_files):
             chat_mouth_cycle = itertools.cycle(img_files)

        try:
            # RAG 체인 생성 및 실행
            chain = get_rag_chain(selected_persona)
            
            # 스트리밍 출력
            # RunnableParallel 구조상 invoke/stream에 문자열을 바로 넘기면 'question'으로 매핑됨 (RunnablePassthrough 덕분)
            # 하지만 안전하게 dict로 넘기는 것이 좋을 수도 있으나, main.py와 동일하게 처리
            stream = chain.stream(prompt)
            
            for chunk in stream:
                full_response += chunk
                msg_container.markdown(f"<p>{full_response}▌</p>", unsafe_allow_html=True)
                
                # 입모양 애니메이션 (이미지가 있을 때만)
                if chat_mouth_cycle:
                    char_container.image(next(chat_mouth_cycle), width=120)
                
                # 너무 빠른 렌더링 방지 (선택사항)
                # time.sleep(0.05) 

            msg_container.markdown(f"<p>{full_response}</p>", unsafe_allow_html=True)
            if os.path.exists("assets/heart_closed.png"):
                char_container.image("assets/heart_closed.png", width=120)

        except Exception as e:
            error_msg = f"죄송합니다. 오류가 발생했습니다: {str(e)}"
            msg_container.error(error_msg)
            full_response = error_msg
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})