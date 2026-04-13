import os
import pandas as pd
from rank_bm25 import BM25Okapi
import ollama
import re

class RAGEngine:
    def __init__(self, drug_name: str, processed_dir: str = "data/processed"):
        self.drug_name = drug_name
        self.corpus_path = os.path.join(processed_dir, drug_name, "corpus.parquet")
        self.df = None
        self.bm25 = None
        self.nodes = []
        self._load_corpus()

    def _load_corpus(self):
        if os.path.exists(self.corpus_path):
            self.df = pd.read_parquet(self.corpus_path)
            self.nodes = self.df['contents'].tolist()
            # Simple tokenization for BM25
            tokenized_corpus = [doc.lower().split() for doc in self.nodes]
            self.bm25 = BM25Okapi(tokenized_corpus)
        else:
            print(f"Corpus not found for {self.drug_name}")

    def retrieve(self, query: str, top_k: int = 3):
        if self.bm25 is None:
            return []
        
        tokenized_query = query.lower().split()
        top_n = self.bm25.get_top_n(tokenized_query, self.nodes, n=top_k)
        
        # Find original rows for metadata if needed
        results = []
        for content in top_n:
            row = self.df[self.df['contents'] == content].iloc[0]
            results.append({
                "content": content,
                "source": row['metadata']['source'],
                "page": row['metadata']['page']
            })
        return results

    def chat(self, query: str, model: str = "qwen3:1.7b"):
        context_docs = self.retrieve(query)
        
        if not context_docs:
            context_text = "No relevant context found in the local knowledge base."
        else:
            context_text = "\n\n".join([f"[Source: {d['source']}, Page: {d['page']}]\n{d['content']}" for d in context_docs])

        system_prompt = f"""You are an elite medical AI assistant.
Your knowledge is based on the provided technical documents for {self.drug_name}.
Use the provided context to answer the user's question accurately and professionally.
If the answer is not in the context, state that you don't have enough information from the local database but provide a general medical perspective if safe.
Respond in professional Korean. Include source references (Source, Page) in your answer if applicable.

Context:
{context_text}
"""
        
        try:
            client = ollama.Client(host='http://127.0.0.1:11434')
            response = client.chat(model=model, messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': query},
            ])
            return response['message']['content'], context_docs
        except Exception as e:
            return f"Error: {str(e)}", []

if __name__ == "__main__":
    # Test
    engine = RAGEngine("default")
    if engine.df is not None:
        ans, docs = engine.chat("이 약의 부작용은 무엇인가요?")
        print(ans)
