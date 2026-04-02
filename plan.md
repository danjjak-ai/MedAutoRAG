# 의료 RAG 시스템 구축 계획서 (plan.md)

이 문서는 `research.md`의 내용을 기반으로 Vibe Coding 방식을 통해 로컬 의료 RAG 시스템(일본어/영어 혼합)을 구축하기 위한 구체적인 실행 계획입니다.

## 1. 프로젝트 개요 및 제약 사항
- **목표:** 일본어와 영어가 혼재된 의료 PDF 문서를 읽고 답변하는 로컬 기반 RAG 시스템 구축
- **하드웨어 환경:** Intel i7, 16GB RAM, Windows (GPU 없음)
- **핵심 전략:**
  - VLM/OCR(PyMuPDF, marker-pdf, moondream)을 바탕으로 복잡한 의료 문서 파싱
  - AutoRAG를 활용한 최적의 RAG 파이프라인 자동 구성 (Medical Taxonomy 반영)
  - CPU 추론을 위한 Ollama 및 GGUF 양자화 모델(llama3.2:3b 등) 사용

## 2. 기술 스택 및 환경 설정 규정
- **추론 엔진:** Ollama (Windows 버전)
- **Local Models:** llama3.2:3b / gemma2:2b (LLM, 2~3GB RAM 점유), moondream (VLM), paraphrase-multilingual-MiniLM-L12-v2 (Embedding)
- **가상 환경:** 기존 환경 구축 폴더가 없다면 **반드시 패키지 매니저 `uv`를 사용하여 `.venv` 가상 환경을 생성**합니다 (`uv venv .venv`). 

## 3. 구현 단계별 스크립트 실행 계획 

### Phase 1: 환경 구성 (Environment Setup) 확인
1. **Ollama 모델 다운로드:** 쉘 스크립트를 통해 필요한 로컬 모델(`llama3.2:3b`, `moondream`) Pull 확인.
2. **가상환경 점검:** `uv` 기반 `.venv` 활성화를 전제로, `requirements.txt`에 `autorag`, `marker-pdf`, `PyMuPDF` 연동.

### Phase 2: PDF Parsing & Text Chunking (Data Preprocessing)
- **스크립트:** `scripts/pdf_parser.py` (신규 작성 예정)
- **작업 내용:**
  - 일본어/영어가 섞인 의료 PDF의 텍스트와 이미지/표를 분리 추출.
  - 표나 차트 등의 이미지는 `moondream` 모델을 활용하여 텍스트 캡션으로 변환.
  - 추출된 텍스트와 캡션을 통합하여 AutoRAG가 인식할 수 있는 마크다운 혹은 `.corpus` 형태로 변환.

### Phase 3: AutoRAG 기반 QA 데이터셋 및 파이프라인 최적화
- **스크립트:** `scripts/data_creator.py` 및 `config/autorag_config.yaml`
- **작업 내용:**
  - **QA 쌍 생성:** 추출된 마크다운을 바탕으로 언어 모델을 활용해 AutoRAG 평가에 사용될 QA Pairs(데이터셋) 자동 생성 (`data_creator.py`).
  - **최적화 설정:** 문맥 윈도우 한계를 고려해 Retrieval Top K는 3~5로 제한하고, 의학 용어 처리에 적합한 **Hybrid Search (BM25 + Vector Search)** 파이프라인을 구축 (`autorag_config.yaml`). CPU 속도를 고려하여 Reranker는 생략하거나 가벼운 모듈 적용. 문장 단위(sentence_window)와 고정 크기(fixed_size) Chunking 모듈 비교 테스트.

### Phase 4: UI 구축 및 테스트
- **스크립트:** `app.py`
- **작업 내용:**
  - Streamlit을 활용하여 질의응답 및 결과 확인이 가능한 간단한 챗봇 환경 UI 구성.
  - 프롬프트에 구체적으로 'Medical Japanese/English translation nuances'를 처리하도록 지시.

## 4. 메모리(16GB) 운영 가이드라인
- VLM 파싱 및 LLM 응답 과정이 CPU 기반에서 Context over limit이 나지 않도록 파이프라인 단위로 메모리 캐싱을 비우거나 가비지 컬렉션을 명시적으로 진행합니다.
- 백그라운드 어플리케이션(Chrome 등) 종료를 권장합니다.

---

> [!IMPORTANT]
> **[확인 요청]**
> 해당 플랜(plan.md)을 기반으로, `uv` 가상환경 세팅 및 첫 번째 `pdf_parser.py` 스크립트 작성 단계로 넘어가도 될지 확인 부탁드립니다.
