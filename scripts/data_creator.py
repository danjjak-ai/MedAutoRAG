import os
import sys
import pandas as pd
import requests
import json
from tqdm import tqdm
import uuid

# Force UTF-8 encoding for console output (Windows fix)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2"
CORPUS_PATH = "data/processed/corpus.parquet"
QA_OUTPUT_PATH = "data/processed/qa.parquet"

def generate_qa_pair(content: str) -> dict:
    """Ask Ollama to generate a QA pair from the given text."""
    prompt = f"""
    Based on the following medical text, generate ONE high-quality question and its corresponding answer.
    The response must be in JSON format with 'query' and 'generation_gt' keys.
    The question should be specific and professional. Respond in Korean.
    
    Text: {content[:1500]}
    
    JSON Output:
    """
    
    try:
        payload = {
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            res_json = response.json().get('response', '')
            return json.loads(res_json)
        return None
    except Exception as e:
        print(f"Error generating QA: {e}")
        return None

def main():
    processed_dir = "data/processed"
    if not os.path.exists(processed_dir):
        print(f"Processed directory not found at {processed_dir}. Run pdf_parser.py first.")
        return

    # 모든 의약품 폴더 탐색
    drug_folders = [d for d in os.listdir(processed_dir) if os.path.isdir(os.path.join(processed_dir, d))]

    for drug in drug_folders:
        corpus_path = os.path.join(processed_dir, drug, "corpus.parquet")
        qa_output_path = os.path.join(processed_dir, drug, "qa.parquet")
        
        if not os.path.exists(corpus_path):
            continue

        print(f"\n--- [{drug}] QA 데이터 세트 생성 중 ---")
        df_corpus = pd.read_parquet(corpus_path)
        qa_data = []

        # 각 의약품별로 최대 10개의 샘플 QA 생성 (테스트용)
        sample_df = df_corpus.sample(min(len(df_corpus), 10))

        for _, row in tqdm(sample_df.iterrows(), total=len(sample_df)):
            qa_pair = generate_qa_pair(row['contents'])
            if qa_pair:
                qa_data.append({
                    "query_id": str(uuid.uuid4()),
                    "query": qa_pair.get('query', ''),
                    "retrieval_gt": [[row['doc_id']]],
                    "generation_gt": [qa_pair.get('generation_gt', '')]
                })

        if qa_data:
            df_qa = pd.DataFrame(qa_data)
            df_qa.to_parquet(qa_output_path, index=False)
            print(f"[{drug}] QA dataset saved to {qa_output_path} ({len(qa_data)} pairs)")
        else:
            print(f"[{drug}] No QA pairs were generated.")

if __name__ == "__main__":
    main()
