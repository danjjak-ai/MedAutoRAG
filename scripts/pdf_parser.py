import os
import sys
import fitz  # PyMuPDF
import json
import base64
import requests
from typing import List, Dict
import pandas as pd
from PIL import Image
import io

# Force UTF-8 encoding for console output (Windows fix)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Ollama API Config
OLLAMA_URL = "http://localhost:11434/api/generate"
VLM_MODEL = "moondream"

def describe_image(image_bytes: bytes) -> str:
    """Send image to Ollama VLM for description."""
    try:
        # Encode image to base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        payload = {
            "model": VLM_MODEL,
            "prompt": "Describe this image in detail, focusing on medical charts, tables, or specialized diagrams. Respond in English.",
            "images": [base64_image],
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            return "[Error: Could not describe image]"
    except Exception as e:
        return f"[Error: {str(e)}]"

def parse_pdf_to_corpus(pdf_path: str, output_folder: str) -> List[Dict]:
    """Parse medical PDF to Markdown and structured fragments."""
    doc = fitz.open(pdf_path)
    base_name = os.path.basename(pdf_path)
    fragments = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text_content = page.get_text("text")
        
        # Image extraction
        image_summaries = []
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            summary = describe_image(image_bytes)
            image_summaries.append(f"\n> [Figure {img_index+1} Description]: {summary}\n")

        # Combine text and image descriptions
        full_content = f"## Page {page_num+1}\n\n" + text_content
        if image_summaries:
            full_content += "\n### Visual Components\n" + "".join(image_summaries)

        fragments.append({
            "doc_id": f"{base_name}_p{page_num+1}",
            "contents": full_content,
            "metadata": {
                "source": base_name,
                "page": page_num + 1
            }
        })

    return fragments

def main():
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    
    # 1. 원본 폴더 내 모든 하위 폴더(의약품명) 탐색
    drug_folders = [d for d in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, d))]
    
    if not drug_folders:
        print("[PROGRESS: 0%] 하위 폴더를 찾을 수 없습니다. 루트 폴더의 PDF 파일만 확인합니다.")
        drug_folders = ["default"]

    total_drugs = len(drug_folders)
    for i, drug in enumerate(drug_folders):
        base_progress = int((i / total_drugs) * 100)
        print(f"\n[PROGRESS: {base_progress}%] --- 의약품 데이터 세트 처리 중: {drug} ---")
        
        drug_raw_path = os.path.join(raw_dir, drug) if drug != "default" else raw_dir
        drug_processed_path = os.path.join(processed_dir, drug)
        os.makedirs(drug_processed_path, exist_ok=True)
        
        pdf_files = [f for f in os.listdir(drug_raw_path) if f.lower().endswith(".pdf")]
        
        if not pdf_files:
            print(f"[PROGRESS: {base_progress}%] {drug} 폴더에 PDF 파일이 없습니다. 건너뜁니다.")
            continue

        drug_corpus = []
        total_files = len(pdf_files)
        for j, pdf_file in enumerate(pdf_files):
            file_progress = base_progress + int((j / total_files) * (100 / total_drugs))
            print(f"[PROGRESS: {file_progress}%] [{drug}] 파싱 중: {pdf_file}")
            path = os.path.join(drug_raw_path, pdf_file)
            fragments = parse_pdf_to_corpus(path, drug_processed_path)
            drug_corpus.extend(fragments)

        # 의약품별 Parquet 저장
        if drug_corpus:
            df = pd.DataFrame(drug_corpus)
            output_path = os.path.join(drug_processed_path, "corpus.parquet")
            df.to_parquet(output_path, index=False)
            print(f"[PROGRESS: {base_progress + int(100/total_drugs)}%] [{drug}] 코퍼스 저장 완료: {output_path}")

    print("\n[PROGRESS: 100%] 모든 RAG 인덱싱 프로세스가 완료되었습니다.")

if __name__ == "__main__":
    main()
