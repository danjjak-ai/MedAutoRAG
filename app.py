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
import sys
from scripts.rag_engine import RAGEngine

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

# Custom CSS for Premium Look & Professional High Visibility
st.markdown("""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        color: #1e293b;
    }
    
    /* Elegant Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
        box-shadow: 4px 0 10px rgba(0,0,0,0.02);
    }
    
    /* High Visibility Professional Buttons */
    div[data-testid="stButton"] button {
        background: linear-gradient(90deg, #0f172a, #1e293b) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
        width: 100%;
    }
    div[data-testid="stButton"] button:hover {
        background: #334155 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        color: #2563eb !important;
        font-weight: 700 !important;
    }

    /* Cards / Chat Messages */
    .stChatMessage {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        margin-bottom: 1rem !important;
    }
    
    .source-box {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 10px;
        margin: 5px 0;
        font-size: 0.85rem;
        border-radius: 4px;
    }

    /* Status Indicators */
    .status-active { color: #10b981; font-weight: bold; }
    .status-idle { color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 20px 0;'><img src='https://img.icons8.com/nolan/128/medical-doctor.png' width='80'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 22px; color: #0f172a; margin-bottom: 5px;'>MedAutoRAG Elite</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 12px; color: #64748b;'>Next-Gen Medical Knowledge Base</p>", unsafe_allow_html=True)
    
    st.divider()

    # Database Selection
    st.subheader("📚 Knowledge Group")
    drugs = get_drug_list()
    selected_drug = st.selectbox("의약품 데이터베이스 선택", drugs, label_visibility="collapsed")
    
    st.divider()

    # Menu
    selected = option_menu(
        None, ["Intelligence Chat", "Data Management", "Analytics Hub", "QA Evaluation", "Settings"],
        icons=["chat-quote", "folder2-open", "graph-up-arrow", "patch-check", "gear"],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"background-color": "transparent", "padding": "0"},
            "icon": {"color": "#3b82f6", "font-size": "16px"},
            "nav-link": {"font-size": "14px", "color": "#475569", "text-align": "left", "margin":"5px 0", "font-weight": "500"},
            "nav-link-selected": {"background-color": "#eff6ff", "color": "#1d4ed8", "border-radius": "8px"},
        }
    )
    
    st.spacer = st.empty()
    st.sidebar.markdown("---")
    # RAM Monitor
    ram = psutil.virtual_memory()
    st.sidebar.caption(f"RAM Usage: {ram.percent}% ({round(ram.used/(1024**3), 1)}G / {round(ram.total/(1024**3), 1)}G)")

# --- Session Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_indexing" not in st.session_state:
    st.session_state.is_indexing = False
if "current_drug" not in st.session_state:
    st.session_state.current_drug = selected_drug

# Reset chat if drug changed
if st.session_state.current_drug != selected_drug:
    st.session_state.messages = []
    st.session_state.current_drug = selected_drug

# --- Backend Utils ---
def is_process_running():
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        if "[PROGRESS: 100%]" in content:
            return False
    return st.session_state.get("is_indexing", False)

def start_indexing():
    if is_process_running():
        return False
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("[START] RAG Indexing started at " + time.ctime() + "\n")
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
        content = "".join(lines[::-1][:15])
        progress_match = re.search(r"\[PROGRESS: (\d+)%\]", content)
        progress = int(progress_match.group(1)) if progress_match else 0
        if "[PROGRESS: 100%]" in "".join(lines):
            st.session_state.is_indexing = False
            return 100, "Indexing Complete."
        return progress, lines[-1].strip()

def render_monitoring_card():
    running = is_process_running()
    if running or st.session_state.get("is_indexing", False):
        progress, status_msg = get_latest_progress()
        st.info(f"⚙️ **Background Indexing Active**: {progress}% - {status_msg}")
        if progress == 100:
            st.success("✅ Indexing complete. Knowledge base refreshed.")

# --- Page Logic ---
if selected == "Intelligence Chat":
    st.markdown(f"### 🧬 AI Medical Intelligence - <span style='color:#1d4ed8'>{selected_drug}</span>", unsafe_allow_html=True)
    render_monitoring_card()
    
    # Init RAG Engine
    @st.cache_resource
    def load_rag(drug):
        return RAGEngine(drug)
    
    rag = load_rag(selected_drug)
    
    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"], unsafe_allow_html=True)

    if prompt := st.chat_input("의학 정보를 문의하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("전문 지식 베이스 검색 및 분석 중..."):
                answer, sources = rag.chat(prompt)
                
                # Format answer with source highlights
                source_html = ""
                if sources:
                    source_html = "<div class='source-box'><b>Reference Sources:</b><br>"
                    for s in sources:
                        source_html += f"• {s['source']} (p.{s['page']})<br>"
                    source_html += "</div>"
                
                full_response = answer + "\n\n" + source_html
                st.markdown(full_response, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

elif selected == "Data Management":
    st.title("📂 Knowledge Assets")
    render_monitoring_card()
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("➕ New Knowledge Group")
        new_name = st.text_input("Group Label", placeholder="e.g. Pfizer_Clinical_Trials")
        if st.button("Create Group"):
            if new_name:
                p = os.path.join(RAW_DIR, new_name)
                if not os.path.exists(p):
                    os.makedirs(p)
                    os.makedirs(os.path.join(PROCESSED_DIR, new_name), exist_ok=True)
                    st.success(f"Group '{new_name}' created.")
                    st.rerun()
    
    with col_r:
        st.subheader("📤 Upload Documents")
        target = st.selectbox("Assign to", get_drug_list())
        files = st.file_uploader("PDF Medical Documents", type="pdf", accept_multiple_files=True)
        if st.button("Submit Upload"):
            if files:
                save_dir = os.path.join(RAW_DIR, target)
                for f in files:
                    with open(os.path.join(save_dir, f.name), "wb") as out:
                        out.write(f.getbuffer())
                st.success(f"{len(files)} files uploaded to {target}.")
    
    st.divider()
    st.subheader("🚀 RAG Pipeline Pipeline Control")
    st.info("Start the automated parser to build the vector index. Uses Moondream VLM for chart/table analysis.")
    if is_process_running():
        st.warning("Indexing is already in progress.")
    else:
        if st.button("RUN FULL INDEXING PIPELINE"):
            if start_indexing():
                st.rerun()

elif selected == "Analytics Hub":
    st.title("📊 Pipeline Analytics")
    render_monitoring_card()
    
    corpus_path = os.path.join(PROCESSED_DIR, selected_drug, "corpus.parquet")
    if os.path.exists(corpus_path):
        df = pd.read_parquet(corpus_path)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Fragments", len(df))
        c2.metric("Source Documents", df['metadata'].apply(lambda x: x['source']).nunique())
        c3.metric("Avg Chunk Size", f"{int(df['contents'].apply(len).mean())} chars")
        
        st.divider()
        st.subheader("Content Distribution by Document")
        doc_counts = df['metadata'].apply(lambda x: x['source']).value_counts()
        st.bar_chart(doc_counts)
        
        st.subheader("Knowledge Sample")
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.warning("No analytics data available for this group. Please run indexing.")

elif selected == "QA Evaluation":
    st.title("🧪 Quality Assurance")
    render_monitoring_card()
    
    qa_path = os.path.join(PROCESSED_DIR, selected_drug, "qa.parquet")
    if os.path.exists(qa_path):
        df_qa = pd.read_parquet(qa_path)
        st.success(f"Golden Dataset found for {selected_drug} with {len(df_qa)} QA pairs.")
        
        st.subheader("Generated Question Snippets")
        for idx, row in df_qa.head(5).iterrows():
            with st.expander(f"Q: {row['query'][:100]}..."):
                st.write(f"**Answer (Ground Truth):** {row['generation_gt'][0]}")
                st.caption(f"Ref ID: {row['retrieval_gt'][0]}")
        
        st.divider()
        if st.button("Run AutoRAG Evaluation (BETA)"):
            st.info("Evaluation process starting... Check terminal for details.")
            # In a real app, this would trigger autorag.evaluate
    else:
        st.subheader("Generate Golden Dataset")
        st.write("Auto-generate a QA dataset from your documents using Llama3.2 to evaluate RAG performance.")
        if st.button("Generate QA Pairs"):
            with st.spinner("Generating..."):
                cmd = [".venv/Scripts/python.exe", "scripts/data_creator.py"]
                subprocess.run(cmd)
                st.rerun()

elif selected == "Settings":
    st.title("⚙️ System Config")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🤖 AI Models")
        st.write("**Chat LLM:** qwen3:1.7b")
        st.write("**Vision VLM:** moondream")
        st.write("**QA Generator:** llama3.2")
        
        if st.button("Check Ollama Connection"):
            try:
                client = ollama.Client(host='http://127.0.0.1:11434')
                client.list()
                st.success("Ollama is ONLINE")
            except:
                st.error("Ollama is OFFLINE")
                
    with col2:
        st.subheader("🖥️ Hardware Info")
        ram = psutil.virtual_memory()
        st.progress(ram.percent / 100)
        st.write(f"RAM: {round(ram.used/(1024**3), 1)}GB / {round(ram.total/(1024**3), 1)}GB")
        st.write(f"Platform: {platform.system()} {platform.release()}")
