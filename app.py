import streamlit as st
from streamlit_option_menu import option_menu
import ollama
import pandas as pd
import os
import requests
import json
from PIL import Image
import base64
import subprocess
import shutil
import time
import re
import psutil
import platform

# Config
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
LOG_DIR = "data/logs"
LOG_FILE = os.path.join(LOG_DIR, "indexing.log")

# Ensure directories
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def get_drug_list():
    folders = [d for d in os.listdir(RAW_DIR) if os.path.isdir(os.path.join(RAW_DIR, d))]
    return sorted(folders) if folders else ["default"]

# --- UI Setup ---
st.set_page_config(
    page_title="MedAutoRAG Elite Pro",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look & Professional High Visibility (Light Theme)
st.markdown("""
<style>
    /* Clean Medical White Background (Reverted from Orange) */
    .stApp {
        background: #ffffff;
        color: #1e293b;
    }
    
    /* Elegant Sidebar (Light Green/Mint) */
    section[data-testid="stSidebar"] {
        background-color: #f0fdf4 !important; /* Soft Light Green */
        border-right: 1px solid #dcfce7;
    }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #065f46 !important; /* Dark Emerald for contrast */
    }

    /* High Visibility Professional Buttons */
    div[data-testid="stButton"] button {
        background: linear-gradient(90deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.7rem 1.4rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] button:hover {
        background: linear-gradient(90deg, #3b82f6, #2563eb) !important;
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2) !important;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        color: #2563eb !important;
        font-weight: 800 !important;
    }

    /* Soft Shadow Cards */
    .stChatMessage, div.stAlert, div[data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        color: #1e293b !important;
    }
    
    /* Fix Input Visibility */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/medical-doctor.png", width=70)
    st.markdown("<h1 style='font-size: 24px; margin-bottom: 0;'>MedAutoRAG</h1>", unsafe_allow_html=True)
    st.caption("Elite Medical Intelligence Platform")
    
    st.divider()

    # Database Selection
    st.subheader("📚 Knowledge Base")
    drugs = get_drug_list()
    selected_drug = st.selectbox("의약품 데이터베이스 선택", drugs)
    
    st.divider()

    # Menu
    selected = option_menu(
        None, ["Medical Chat", "Data Management", "Dashboard", "Evaluation", "System Settings"],
        icons=["chat-dots", "cloud-upload", "activity", "clipboard-check", "sliders"],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"background-color": "transparent", "padding": "0"},
            "icon": {"color": "#10b981", "font-size": "18px"},
            "nav-link": {"font-size": "15px", "color": "#065f46", "text-align": "left", "margin":"5px 0", "--hover-color": "rgba(0,0,0,0.05)"},
            "nav-link-selected": {"background-color": "#dcfce7", "color": "#064e3b", "border-left": "4px solid #10b981"},
        }
    )

# --- Session Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_indexing" not in st.session_state:
    st.session_state.is_indexing = False

# --- Backend Utils ---
def is_process_running():
    # Simple check: if log exists and has [PROGRESS: 100%] it's done
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        if "[PROGRESS: 100%]" in content:
            return False
    # Check if a python process running pdf_parser is alive (Platform dependent, here simple approach)
    return st.session_state.get("is_indexing", False)

def start_indexing():
    if is_process_running():
        return False
    
    # Clear log
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("[START] RAG Indexing started at " + time.ctime() + "\n")
    
    # Run in background
    cmd = [".venv/Scripts/python.exe", "scripts/pdf_parser.py"]
    with open(LOG_FILE, "a", encoding="utf-8") as log_f:
        subprocess.Popen(cmd, stdout=log_f, stderr=log_f, shell=False)
    
    st.session_state.is_indexing = True
    return True

def get_latest_progress():
    if not os.path.exists(LOG_FILE):
        return 0, "No progress data."
    
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines: return 0, "Initializing..."
        
        last_line = lines[-1].strip()
        progress_match = re.search(r"\[PROGRESS: (\d+)%\]", "".join(lines[::-1][:10])) # Check last 10 lines
        progress = int(progress_match.group(1)) if progress_match else 0
        
        if "[PROGRESS: 100%]" in "".join(lines):
            st.session_state.is_indexing = False
            return 100, "Indexing Complete."
            
        return progress, last_line

# --- Monitoring Component (Used in multiple pages) ---
def render_monitoring_card():
    running = is_process_running()
    if running or (os.path.exists(LOG_FILE) and st.session_state.get("is_indexing_last", True)):
        progress, status_msg = get_latest_progress()
        
        with st.container():
            st.markdown("### 🔄 RAG Indexing Monitor")
            col1, col2 = st.columns([4, 1])
            col1.progress(progress / 100)
            col2.write(f"**{progress}%**")
            st.caption(f"Status: {status_msg}")
            
            with st.expander("상세 로그 보기"):
                if os.path.exists(LOG_FILE):
                    with open(LOG_FILE, "r", encoding="utf-8") as f:
                        st.code(f.read()[-2000:], language="text")
        
        if progress == 100:
            st.session_state.is_indexing_last = False
            st.success("✅ 인덱싱이 완료되었습니다. 새로운 데이터가 반영되었습니다.")

# --- Page Logic ---
if selected == "Medical Chat":
    st.title("🧬 Intelligence Chat")
    render_monitoring_card()
    
    # Chat logic
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("의료 질문 또는 분석 요청..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("로컬 지식 베이스 분석 중..."):
                try:
                    # 명시적인 호스트 주소 사용 (127.0.0.1)
                    client = ollama.Client(host='http://127.0.0.1:11434')
                    response = client.chat(model='qwen3:1.7b', messages=[
                        {'role': 'system', 'content': f'Elite medical AI specializing in {selected_drug}. Use professional Korean.'},
                        {'role': 'user', 'content': prompt},
                    ])
                    ans = response['message']['content']
                    st.write(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                except Exception as e:
                    st.error(f"Ollama 연결 실패 (127.0.0.1:11434): {e}")
                    st.info("터미널에서 'ollama list'를 입력하여 qwen3:1.7b 또는 llama3.2 모델이 있는지 확인해 주세요.")

elif selected == "Data Management":
    st.title("📂 Data & Knowledge Management")
    render_monitoring_card()
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown("#### 🆕 의약품 그룹 등록")
        new_name = st.text_input("신규 의약품명", placeholder="예: Drug_A_Release")
        if st.button("그룹 생성"):
            if new_name:
                p = os.path.join(RAW_DIR, new_name)
                if not os.path.exists(p):
                    os.makedirs(p)
                    os.makedirs(os.path.join(PROCESSED_DIR, new_name), exist_ok=True)
                    st.success(f"'{new_name}' 그룹이 등록되었습니다.")
                    st.rerun()
                else: st.warning("이미 존재합니다.")

    with col_r:
        st.markdown("#### 📤 문서 업로드")
        target = st.selectbox("업로드 대상", get_drug_list())
        files = st.file_uploader("PDF 업로드", type="pdf", accept_multiple_files=True)
        if st.button("파일 업로드 실행"):
            if files:
                save_dir = os.path.join(RAW_DIR, target)
                for f in files:
                    with open(os.path.join(save_dir, f.name), "wb") as out:
                        out.write(f.getbuffer())
                st.success(f"{len(files)}개 문서가 '{target}'에 저장되었습니다.")
            else: st.error("파일을 선택하세요.")

    st.divider()
    st.markdown("#### 🚀 RAG 파이프라인 제어")
    st.write("문서 업로드 후 아래 버튼을 클릭하면 백그라운드 인덱싱이 시작됩니다.")
    
    if is_process_running():
        st.info("⚠️ 현재 다른 인덱싱 작업이 진행 중입니다.")
        if st.button("새로고침"): st.rerun()
    else:
        if st.button("RAG 처리 시작 (Start Background Indexing)"):
            if start_indexing():
                st.session_state.is_indexing_last = True
                st.success("인덱싱 프로세스가 백그라운드에서 시작되었습니다. 대시보드나 다른 메뉴에서 상태를 확인하세요.")
                st.rerun()

elif selected == "Dashboard":
    st.title("📊 System Analytics Dashboard")
    render_monitoring_card()
    
    st.markdown("#### 🧪 Database Statistics")
    # Quick Summary
    corpus_path = os.path.join(PROCESSED_DIR, selected_drug, "corpus.parquet")
    if os.path.exists(corpus_path):
        df = pd.read_parquet(corpus_path)
        k1, k2, k3 = st.columns(3)
        k1.metric("총 지식 파편(Fragments)", len(df))
        k2.metric("소스 문서 수", df['metadata'].apply(lambda x: x['source']).nunique())
        k3.metric("평균 응답 품질", "High")
    else:
        st.warning("선택된 의약품에 대한 인덱싱 데이터가 없습니다.")

elif selected == "Evaluation":
    st.title("🧪 Pipeline Evaluation")
    render_monitoring_card()
    st.write("자동 생성된 평가용 QA 셋을 기반으로 검색 및 생성 성능을 검증합니다.")
    st.info("이 기능은 백그라운드 인덱싱 완료 후 사용 가능합니다.")

elif selected == "System Settings":
    st.title("⚙️ System & AI Settings")
    render_monitoring_card()
    
    # 1. System Hardware Info
    st.subheader("🖥️ Local Hardware Status")
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        cpu_usage = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = shutil.disk_usage(".")
        
        col1.metric("CPU Usage", f"{cpu_usage}%")
        col2.metric("RAM Usage", f"{ram.percent}%", f"{round(ram.used/(1024**3), 1)}GB / {round(ram.total/(1024**3), 1)}GB")
        col3.metric("Disk Free", f"{round(disk.free/(1024**3), 1)}GB", f"Total: {round(disk.total/(1024**3), 1)}GB")
        col4.metric("OS", platform.system(), platform.release())
    except Exception as e:
        st.error(f"시스템 정보를 가져오는 중 오류가 발생했습니다: {e}")
    
    st.divider()
    
    # 2. Ollama Model Management
    st.subheader("🤖 Ollama Model Explorer")
    try:
        # Get models
        models_data = ollama.list()
        # The structure of ollama.list() can vary by version, handling carefully
        models = models_data.get('models', [])
        if models:
            model_list = []
            for m in models:
                name = m.get('name', 'Unknown')
                size = m.get('size', 0)
                modified = m.get('modified_at', "Unknown")
                if isinstance(modified, str): modified = modified.split("T")[0]
                
                model_list.append({
                    "Model Name": name,
                    "Size (GB)": round(size / (1024**3), 2),
                    "Modified": modified
                })
            df_models = pd.DataFrame(model_list)
            st.dataframe(df_models, use_container_width=True)
        else:
            st.warning("설치된 Ollama 모델이 없습니다.")
    except Exception as e:
        st.error(f"Ollama 모델 정보를 가져오지 못했습니다: {e}")
    
    st.divider()
    
    # 3. RAG Data Statistics
    st.subheader("📊 RAG Knowledge Stats")
    drugs = get_drug_list()
    total_raw_pdfs = 0
    total_indexed_drugs = 0
    
    for d in drugs:
        raw_p = os.path.join(RAW_DIR, d)
        proc_p = os.path.join(PROCESSED_DIR, d)
        if os.path.exists(raw_p):
            total_raw_pdfs += len([f for f in os.listdir(raw_p) if f.endswith('.pdf')])
        if os.path.exists(proc_p) and any(os.path.isdir(os.path.join(proc_p, i)) for i in os.listdir(proc_p)):
            total_indexed_drugs += 1
            
    c1, c2, c3 = st.columns(3)
    c1.metric("Registered Drugs", len(drugs))
    c2.metric("Total Raw PDFs", total_raw_pdfs)
    c3.metric("Fully Indexed Drugs", total_indexed_drugs)

    with st.expander("🛠️ Advanced System Details"):
        st.json({
            "Python Version": sys.version,
            "Streamlit Version": st.__version__,
            "Processor": platform.processor(),
            "Machine": platform.machine(),
            "Current Directory": os.getcwd()
        })
