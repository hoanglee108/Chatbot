import faiss
import numpy as np
from embed import create_embeddings, load_data
from sentence_transformers import SentenceTransformer

class Chatbot:
    def __init__(self, csv_path):
        self.df = load_data(csv_path)
        self.contents, self.embeddings = create_embeddings(self.df)
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(self.embeddings)

    def search(self, query, top_k=3):
        query_vec = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vec), top_k)
        results = []
        for idx in indices[0]:
            results.append({
                "title": self.df.iloc[idx]['title'],
                "description": self.df.iloc[idx]['description'],
                "ingredients": self.df.iloc[idx]['ingredients'],
                "steps": self.df.iloc[idx]['steps'],
                "usage": self.df.iloc[idx]['usage'],
                "tips": self.df.iloc[idx]['tips'],
                "url": self.df.iloc[idx]['url'],
            })
        return results
