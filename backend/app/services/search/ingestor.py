import os
import json
import faiss
import numpy as np
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_DIR = os.path.join(BASE_DIR, "vector_db")
model = SentenceTransformer('all-MiniLM-L6-v2')

class DocumentIngestor:
    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        self.faiss_path = os.path.join(DB_DIR, "faiss_index.bin")
        self.metadata_path = os.path.join(DB_DIR, "metadata.json")

    def process_pdf(self, file_path):
        reader = PdfReader(file_path)
        chunks = []
        
        # We will use 800 characters per chunk, with 200 characters of overlap!
        CHUNK_SIZE = 800
        OVERLAP = 200

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                # Clean up weird PDF spacing
                text = " ".join(text.split())
                
                # Create overlapping chunks
                start = 0
                while start < len(text):
                    end = start + CHUNK_SIZE
                    chunk = text[start:end].strip()
                    
                    if len(chunk) > 50: # Only save chunks that actually have data
                        chunks.append({
                            "source": os.path.basename(file_path),
                            "page": page_num + 1,
                            "text": chunk
                        })
                    # Move forward, but step back by the OVERLAP amount
                    start += (CHUNK_SIZE - OVERLAP)
                    
        return chunks

    def update_vector_db(self, new_chunks):
        if not new_chunks: return 0
        
        texts = [c["text"] for c in new_chunks]
        new_embeddings = model.encode(texts)
        new_embeddings = np.array(new_embeddings).astype('float32')

        # Load existing FAISS index or create a new one
        if os.path.exists(self.faiss_path):
            index = faiss.read_index(self.faiss_path)
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            index = faiss.IndexFlatL2(new_embeddings.shape[1])
            metadata = []

        index.add(new_embeddings)
        metadata.extend(new_chunks)

        faiss.write_index(index, self.faiss_path)
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)

        return len(new_chunks)

doc_ingestor = DocumentIngestor()