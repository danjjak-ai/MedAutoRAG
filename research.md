research.md: Local Medical RAG Construction (JP/EN)
1. Project Overview
Goal: Build a local RAG system for medical PDFs (Japanese/English mix).
Hardware: Intel i7, 16GB RAM, Windows (No GPU).
Core Strategy:
Vision-based Parsing: Convert complex medical PDFs to markdown using a light VLM or OCR.
AutoRAG Optimization: Automatically find the best RAG pipeline (Chunking/Retriever) for medical terminology.
CPU Inference: Use Ollama with GGUF-quantized models to fit within 16GB RAM.
2. Tech Stack & Environment
Inference Engine: Ollama (Windows version)
RAG Framework: AutoRAG
Local Models (CPU Optimized):
LLM: llama3.2:3b or gemma2:2b (Fits in ~2-3GB RAM)
VLM (Parsing): moondream (Very small, for describing medical charts/tables)
Embedding: paraphrase-multilingual-MiniLM-L12-v2 (Fast on CPU)
Data Parsing: marker-pdf or PyMuPDF (Better for JP/EN layout)
3. Implementation Steps
Phase 1: Environment Setup
Install Ollama and pull models:
bash
ollama pull llama3.2:3b
ollama pull moondream
Use code with caution.

Create a Python virtual environment and install AutoRAG:
bash
pip install autorag marker-pdf
Use code with caution.

Phase 2: Data Preprocessing (Vision-to-Text)
Objective: Convert medical PDFs into clean Markdown.
Process:
Use marker to extract text from JP/EN PDFs.
For pages with complex diagrams, use moondream via Ollama to generate text descriptions of images.
Store the result as a .corpus file for AutoRAG.
Phase 3: AutoRAG Pipeline Optimization
Config: Create config.yaml for AutoRAG.
Key Modules to Test:
Chunking: sentence_window, fixed_size.
Retrieval: Hybrid Search (BM25 for medical terms + Vector for semantic meaning).
Reranker: upr or tart (only if CPU speed allows).
Phase 4: Integration & Vibe Coding
Use a frontend (e.g., Streamlit or a simple CLI) to query the medical documents.
Ensure the prompt template specifically instructs the LLM to handle Medical Japanese/English translation nuances.
4. Constraint Check (16GB RAM Management)
Disable all background heavy apps (Chrome, etc.).
Use Quantized GGUF models only.
Limit the top_k retrieval to 3-5 snippets to prevent context window overflow on CPU.
5. Next Actions for AI Agent
Script 1: Write a PDF parser using marker or PyMuPDF that outputs structured markdown.
Script 2: Create the AutoRAG data_creation script to transform markdown into AutoRAG-compatible QA pairs.
Script 3: Generate the config.yaml for a "Hybrid Search" pipeline optimized for multilingual medical terms.