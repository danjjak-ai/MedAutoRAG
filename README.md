# MedAutoRAG: Local Medical RAG System
[English] | [한국어](#한국어) | [日本語](#日本語)

MedAutoRAG is a high-performance local medical knowledge base and RAG (Retrieval-Augmented Generation) system that operates entirely offline. It is designed to analyze sensitive medical data using local LLMs without external data leakage.

## 🌟 Key Features

- **Local LLM Powered (Ollama)**: Uses state-of-the-art lightweight models like `Llama 3.2`, `Qwen`, and `Moondream` via Ollama, ensuring data privacy and security.
- **Medical Knowledge Base**: Upload and manage PDF documents categorized by drug groups.
- **Hybrid Search**: Combines BM25 and Semantic Search for high precision in complex medical terminology.
- **Real-time Monitoring**: Premium UI with indexing progress, system resource status (CPU/RAM), and model information.
- **16GB RAM Optimized**: Designed to run smoothly even in non-GPU environments using efficient memory management.

## 🛠️ Tech Stack

- **UI**: Streamlit (Premium Custom CSS)
- **RAG Engine**: AutoRAG (Local Integration)
- **Model Management**: Ollama
- **PDF Parsing**: PyMuPDF + Moondream (VLM for Image/Table Captioning)
- **Package Manager**: `uv`

---

## <a name="한국어"></a>🇰🇷 한국어

MedAutoRAG는 인터넷 연결 없이 로컬 환경에서 작동하는 고성능 의료 지식 베이스 및 RAG 시스템입니다.

### 🌟 주요 특징
- **로컬 LLM 기반 (Ollama)**: `Llama 3.2`, `Qwen`, `Moondream` 등을 사용하여 보안성 보장.
- **의료 지식 베이스 관리**: PDF 문서를 의약품별로 그룹화하여 관리.
- **하이브리드 검색**: BM25와 세만틱 검색 결합으로 의학 용어 검색 성능 극대화.
- **프리미엄 UI**: 실시간 인덱싱 현황 및 시스템 자원 모니터링 제공.

---

## <a name="日本語"></a>🇯🇵 日本語

MedAutoRAGは、インターネット接続なしで完全オフラインで動作する高性能なローカル医療ナレッジベースおよびRAGシステムです。

### 🌟 主な特徴
- **ローカルLLM（Ollama）**: `Llama 3.2`、`Qwen`、`Moondream`などの軽量モデルを使用し、データの機密性を保持。
- **医療ナレッジベース管理**: 医薬品ごとにPDFドキュメントをグループ化して管理。
- **ハイブリッド検索**: BM25とセマンティック検索を組み合わせ、専門的な医療用語に対して高い検索精度を実現。
- **プレミアムUI**: インデックス作成の進行状況、システムリソース（CPU/RAM）、モデル情報をリアルタイムで表示。

---

## 🚀 Getting Started / 시작하기 / 始め方

### 📋 Prerequisites
1. Install [Ollama](https://ollama.com/)
2. Pull required models:
   ```bash
   ollama pull llama3.2
   ollama pull moondream
   ollama pull qwen3:1.7b
   ```

### ⚙️ Installation
```bash
# Clone and setup env
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt

# Run
run_app.bat
```

## 📁 Project Structure
```text
MedAutoRAG/
├── app.py              # Main Streamlit Dashboard
├── scripts/
│   ├── pdf_parser.py   # PDF Extraction & Processing
│   ├── rag_engine.py   # Retrieval & Generation Engine
│   └── data_creator.py # QA Dataset Generation Tool
├── config/
│   └── autorag_config.yaml # Pipeline Configuration
└── data/
    ├── raw/            # Uploaded PDF Source
    └── processed/      # Indexing & Parquet Corpus
```

---
*Developed with ❤️ for Medical Intelligence.*
