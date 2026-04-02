# 로컬 의료 RAG 시스템 (MedAutoRAG) 구축 계획

`research.md`, `plan.md`, `UIX.md`를 바탕으로, 로컬 환경(Intel i7, 16GB RAM, Windows, No GPU)에서 작동하는 다국어(일/영) 의료 RAG 시스템을 구축합니다.

## 제약 사항 및 전략
- **하드웨어**: 16GB RAM 제한에 따라 가벼운 모델(`llama3.2:3b`, `moondream`) 사용.
- **보안**: 로컬 LLM(Ollama) 사용으로 데이터 외부 유입 차단.
- **성능**: Hybrid Search(BM25 + Semantic Search)로 의학 용어 검색 정확도 향상.
- **디자인**: Streamlit의 한계를 넘는 프리미엄 UI/UX 적용.

## 1단계: 개발 환경 및 모델 준비 (Phase 1)
- [ ] **가상환경**: `uv`를 사용하여 `.venv` 생성 및 활성화.
- [ ] **패키지 설치**: `autorag`, `marker-pdf`, `pymupdf`, `streamlit`, `ollama` 등 설치.
- [ ] **로컬 모델**: Ollama를 통해 `llama3.2:3b`, `moondream` 모델 Pull. (v0.19.0 확인됨)

## 2단계: 데이터 전처리 플로우 (Phase 2)
- [ ] **PDF 파서 (`scripts/pdf_parser.py`)**:
    - PyMuPDF 기반 텍스트 추출.
    - `moondream`(VLM)을 이용한 이미지/표 텍스트 캡션 생성.
    - 결과물을 AutoRAG 호환 마크다운 파일로 저장.

## 3단계: AutoRAG 파이프라인 및 데이터셋 구성 (Phase 3)
- [ ] **QA 데이터 생성 (`scripts/data_creator.py`)**:
    - 추출된 마크다운에서 LLM을 이용해 질문-답변(QA) 쌍 자동 생성.
- [ ] **파이프라인 설정 (`config/autorag_config.yaml`)**:
    - 최적의 Chunking 전략(sentence_window 등) 설정.
    - CPU 환경을 고려한 Retrieval Top K (3~5) 및 Hybrid Search 설정.

## 4단계: 반복적 검색 성능 검증 및 개선 (Evaluation Loop) [NEW]
- [ ] **성능 측정 도구 (AutoRAG Dashboard)**: 
    - AutoRAG의 `evaluate` 기능을 활용하여 `Retriever`와 `Generator`의 정밀도(Precision), 재현율(Recall), F1-score 측정.
- [ ] **반복적 개선 프로세스**:
    - **QA 데이터셋 고도화**: LLM을 통해 생성된 골든 데이터셋(Golden Dataset)을 인간이 검토/수정하여 기준점 확보.
    - **하이퍼파라미터 튜닝**: Chunk size, Top K, Hybrid Search 가중치 등을 조정하며 최적의 조합 탐색.
    - **실패 사례 분석 (Error Analysis)**: 답변이 틀린 케이스를 분석하여 프롬프트 템플릿(System Prompt) 고도화.

## 5단계: 프리미엄 UI/UX 개발 (app.py) [UPDATED]
- [ ] **디자인 철학**: 현대적이고 신뢰감 있는 의료 전문가용 대시보드 디자인 (High-end Aesthetic).
- [ ] **기술적 구현**:
    - **Custom CSS**: Glassmorphism, 부드러운 애니메이션, 세련된 타이포그래피 적용.
    - **레이아웃**: `streamlit-option-menu` 등을 활용한 직관적인 사이드바 내비게이션.
    - **데이터 시각화**: 인덱싱 상태, 성능 지표(Accuracy/Latency) 등을 차트와 그래프로 시각화.
- [ ] **주요 기능**:
    - 실시간 인덱싱 로그 및 상태 대시보드.
    - 출처(Source Reference)의 원문 하이라이트 미리보기 기능.
    - 메모리 및 모델 상태 모니터링 (16GB RAM 최적화 정보 표시).

---

## 사용자 확인 사항
> [!IMPORTANT]
> 1. **UI 라이브러리**: Streamlit에서 최고 수준의 커스텀을 시도하겠습니다. (필요 시 Next.js 검토 가능하나 우선 순위는 로컬 실행 편의성입니다.)
> 2. **성능 개선**: 반복적 개선을 위해 초기 샘플 문서를 최소 5~10개 정도 준비해 주시면 더욱 정확한 테스트가 가능합니다.

## 자동화 검증 계획
- `pdf_parser.py` 실행 후 마크다운 파일 생성 확인.
- AutoRAG 구성 후 검증용 QA 데이터셋 기반 검색 성능 측정 및 리포트 자동 생성.
- UI 앱의 프리미엄 테마 및 챗봇 질의응답 정상 작동 확인.
