# MedAutoRAG: Local Medical RAG System
[English] | [한국어](#한국어) | [日本語](#日本語)

MedAutoRAG is a high-performance local medical knowledge base and RAG (Retrieval-Augmented Generation) system that operates entirely offline for daily tasks and leverages Google Colab for heavy processing. It is designed to analyze sensitive medical data using local LLMs without external data leakage.

## 🌟 Key Features

- **Next-Gen LLM Powered (Gemma 4)**: Uses the latest `Gemma 4 (e2b)` model via Ollama, offering superior medical reasoning and translation performance.
- **Hybrid Inference (Local + Colab)**:
    - **Local**: Daily chat and simple indexing (CPU/RAM optimized).
    - **Cloud (Google Colab)**: GPU-intensive tasks like VLM parsing (Gemma4-Vision) and AutoRAG optimization via a built-in UI dashboard.
- **Medical Knowledge Base**: Upload and manage PDF documents categorized by drug groups.
- **Hybrid Search**: Combines BM25 and Semantic Search for high precision in complex medical terminology.
- **Real-time Monitoring**: Premium UI with indexing progress, system resource status (CPU/RAM), and model information.
- **16GB RAM Optimized**: Designed to run smoothly even in non-GPU environments using efficient memory management.

## 📸 UI Gallery

````carousel
![Intelligence Chat](assets/screenshots/chat.png)
<!-- slide -->
![Data Management](assets/screenshots/data.png)
<!-- slide -->
![Cloud Processing](assets/screenshots/cloud.png)
<!-- slide -->
![Analytics Hub](assets/screenshots/analytics.png)
<!-- slide -->
![QA Evaluation](assets/screenshots/qa.png)
<!-- slide -->
![Settings](assets/screenshots/settings.png)
````

## 🛠️ Tech Stack

- **UI**: Streamlit (Premium Custom CSS)
- **Hybrid Compute**: Local CPU + Google Colab (GPU Integration)
- **RAG Engine**: AutoRAG (Local Integration)
- **Model Management**: Ollama
- **PDF Parsing**: PyMuPDF + Gemma 4 (Multimodal VLM for Image/Table Captioning)
- **Package Manager**: `uv`

---

## <a name="한국어"></a>🇰🇷 한국어

MedAutoRAG는 인터넷 연결 없이 로컬 환경에서 작동하는 고성능 의료 지식 베이스 및 RAG 시스템입니다. 리소스가 많이 필요한 작업은 구글 Colab과 병행하여 최상의 성능을 제공합니다.

### 🌟 주요 특징
- **차세대 LLM 기반 (Gemma 4)**: 최신 `Gemma 4 (e2b)` 모델을 사용하여 정교한 의학적 추론 및 번역 성능 보장.
- **하이브리드 인퍼런스 (로컬 + Colab)**:
    - **로컬**: 일상적 대화 및 기본 인덱싱 (CPU 최적화).
    - **클라우드 (Google Colab)**: VLM 파싱 및 AutoRAG 최적화 등 고부하 작업을 위한 전용 UI 대시보드 제공.
- **의료 지식 베이스 관리**: PDF 문서를 의약품별로 그룹화하여 관리.
- **하이브리드 검색**: BM25와 세만틱 검색 결합으로 의학 용어 검색 성능 극대화.
- **프리미엄 UI**: 실시간 인덱싱 현황 및 클라우드 데이터 Export/Import 기능 제공.

---

## <a name="日本語"></a>🇯🇵 日本語

MedAutoRAGは、完全オフラインで動作する高性能なローカル医療ナレッジベースおよびRAGシステムです。Google Colabとの連携により、リソース集約型のタスクもスムーズに処理可能です。

### 🌟 主な特徴
- **次世代LLM（Gemma 4）**: 最新の `Gemma 4 (e2b)` モデルを使用し、高度な医療推論と翻訳性能を実現。
- **ハイブリッド・インフェレンス（ローカル + Colab）**:
    - **ローカル**: 日常的なチャットと基本的なインデックス作成（CPU/RAM最適化）。
    - **クラウド（Google Colab）**: VLMパースやAutoRAG最適化などの重いタスクを処理するための専用UIダッシュボードを搭載。
- **医療ナレッジベース管理**: 医薬品ごとにPDFドキュメントをグループ化して管理。
- **ハイブリッド検索**: BM25とセマンティック検索を組み合わせ、複雑な医療用語に対しても高い精度で検索。
- **プレミアムUI**: リアルタイムの進行状況モニタリング、クラウドデータのエクスポート/インポート機能。

---

## 🚀 Getting Started / 시작하기 / 始め方

### 📋 Prerequisites
1. Install [Ollama](https://ollama.com/)
2. Pull required models:
   ```bash
   ollama pull gemma4:e2b
   ollama pull gemma4
   ollama pull moondream
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
├── app.py              # Main Streamlit Dashboard (Local + Cloud UI)
├── scripts/
│   ├── pdf_parser.py   # PDF Extraction (Gemma 4 Vision supported)
│   ├── rag_engine.py   # Retrieval & Generation Engine (Gemma 4 default)
│   └── data_creator.py # QA Dataset Generation Tool
├── config/
│   └── autorag_config.yaml # Pipeline Configuration
└── data/
    ├── raw/            # Uploaded PDF Source
```

---
*Developed with ❤️ for Medical Intelligence.*
