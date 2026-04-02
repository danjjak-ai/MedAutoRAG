# MedAutoRAG: 로컬 의료 RAG 시스템 (Elite Medical Intelligence Platform)

MedAutoRAG는 인터넷 연결 없이 로컬 환경에서 작동하는 고성능 의료 지식 베이스 및 RAG(Retrieval-Augmented Generation) 시스템입니다. 보안이 중요한 의료 데이터를 외부 유출 없이 로컬 LLM을 통해 분석할 수 있도록 설계되었습니다.

## 🌟 주요 특징

- **로컬 LLM 기반 (Ollama)**: 인터넷 연결 없이 `Llama 3.2`, `Qwen`, `Moondream` 등 최신 경량 LLM을 사용하여 개인정보 및 연구 데이터 보안을 보장합니다.
- **의료 지식 베이스 관리**: PDF 문서를 업로드하고 의약품별로 그룹화하여 관리할 수 있습니다.
- **하이브리드 검색 (Hybrid Search)**: BM25와 세만틱 검색을 결합하여 복잡한 의학 용어에 대해서도 높은 검색 정확도를 제공합니다.
- **실시간 모니터링 대시보드**: 인덱싱 진행 상황, 시스템 자원(CPU/RAM) 상태, 모델 정보 등을 한눈에 확인할 수 있는 프리미엄 UI를 제공합니다.
- **16GB RAM 최적화**: GPU가 없는 환경에서도 원활하게 작동하도록 경량 모델 및 효율적인 메모리 관리 전략을 사용합니다.

## 🛠️ 기술 스택

- **Backend Logic**: Python 3.x
- **Frontend UI**: Streamlit (Premium Custom CSS)
- **RAG Engine**: AutoRAG (Local Integration)
- **Deep Learning Model Management**: Ollama
- **PDF Parsing**: PyMuPDF + Moondream (VLM for Image/Table Captioning)
- **Package Manager**: `uv` (Fast & Reproducible environment)

## 📁 프로젝트 구조

```text
MedAutoRAG/
├── app.py              # Streamlit 메인 대시보드 애플리케이션
├── requirements.txt    # 의존성 패키지 목록
├── .gitignore          # Git 제외 파일 설정
├── data/
│   ├── raw/            # 업로드된 원본 PDF 파일 (의약품별 그룹화)
│   ├── processed/      # AutoRAG 인덱싱 결과물
│   └── logs/           # 시스템 및 인덱싱 로그
├── scripts/
│   ├── pdf_parser.py   # PDF 텍스트/이미지 추출 및 전처리 스크립트
│   └── data_creator.py # QA 데이터셋 생성 도구
├── config/
│   └── autorag_config.yaml # AutoRAG 검색 파이프라인 설정
└── run_app.bat         # 윈도우 실행용 배치 파일
```

## 🚀 시작하기

### 📋 사전 요구 사항

1. [Ollama](https://ollama.com/) 설치 및 실행
2. 필요한 모델 다운로드:
   ```bash
   ollama pull llama3.2:3b
   ollama pull moondream
   ollama pull qwen3:1.7b  # (또는 설정된 모델)
   ```

### ⚙️ 설치 및 실행

1. **저장소 복제 및 가상환경 설정** (uv 사용 권장):
   ```bash
   uv venv
   .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

2. **애플리케이션 실행**:
   ```bash
   run_app.bat
   # 또는 직접 실행:
   streamlit run app.py
   ```

## 📈 사용 방법

1. **의약품 등록**: `Data Management` 메뉴에서 분석할 의약품 그룹을 생성합니다.
2. **문서 업로드**: 관련 전문 의학 PDF 문서를 업로드합니다.
3. **인덱싱 시작**: `Start Background Indexing`을 눌러 RAG 파이프라인을 구축합니다. (백그라운드에서 진행되며 대시보드에서 상태 확인 가능)
4. **질의응답**: `Medical Chat` 메뉴에서 해당 의약품에 대한 전문적인 질문을 수행합니다.

## 🛡️ 라이선스

본 프로젝트는 연구 및 내부용으로 개발되었습니다.

---
*Developed with ❤️ for Medical Intelligence.*
