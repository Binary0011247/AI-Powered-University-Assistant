import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticSearchEngine:
    def __init__(self):
        # Get absolute paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.db_dir = os.path.join(self.base_dir, "vector_db")
        self.faiss_path = os.path.join(self.db_dir, "faiss_index.bin")
        self.metadata_path = os.path.join(self.db_dir, "metadata.json")

        print("🔍 Loading Semantic Search Engine...")
        # 1. Load the same AI model we used for ingestion
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 2. Load the FAISS database and the text metadata
        if os.path.exists(self.faiss_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.faiss_path)
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            print(f"✅ Search Engine Ready! Loaded {self.index.ntotal} documents.")
        else:
            print("⚠️ WARNING: FAISS database not found. Run ingest_data.py first.")
            self.index = None
            self.metadata = []

    def search(self, query: str, top_k: int = 2):
        if self.index is None or self.index.ntotal == 0:
            return ["I'm sorry, my knowledge base is currently empty."]

        # 1. Convert the user's question into a Vector
        query_vector = self.model.encode([query])
        query_vector = np.array(query_vector).astype('float32')

        # 2. Search FAISS for the 'top_k' closest matches
        distances, indices = self.index.search(query_vector, top_k)

        # 3. Retrieve the actual text for those matches
        results = []
        for i in range(top_k):
            idx = indices[0][i]
            if idx != -1 and idx < len(self.metadata): # -1 means no match found
                results.append(self.metadata[idx]["text"])
                
        return results

# Create a single instance to be used across the app
search_engine = SemanticSearchEngine()