@echo off
setlocal
cd /d %~dp0

echo [1/3] 가상환경(.venv) 확인 중...
if not exist ".venv" (
    echo [ERROR] 가상환경이 존재하지 않습니다. uv venv .venv를 먼저 실행하세요.
    pause
    exit /b
)

echo [2/3] Ollama 서비스 연결 확인 중...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama 서비스가 실행 중이지 않거나 응답하지 않습니다.
    echo Ollama를 먼저 실행해 주세요.
)

echo [3/3] MedAutoRAG 프리미엄 대시보드 실행 중...
call .venv\Scripts\activate.bat
streamlit run app.py

pause
