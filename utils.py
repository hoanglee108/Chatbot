import pandas as pd
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from api import model  # model Gemini khởi tạo trong api.py

# Load dữ liệu và chuyển thành documents
def row_to_document(row):
    return f"""Tên món: {row['title']}
Nguyên liệu: {row.get('ingredients', '')}
Cách làm: {row.get('steps', '')}
Cách dùng: {row.get('usage', '')}
Mẹo nhỏ: {row.get('tips', '')}"""

def load_and_prepare_documents(json_path):
    df = pd.read_json(json_path, encoding="utf-8-sig")
    documents = df.apply(row_to_document, axis=1).tolist()
    return df, documents

# Tạo embeddings
class Retriever:
    def __init__(self, documents, model_name="all-MiniLM-L6-v2"):
        self.documents = documents
        self.embedder = SentenceTransformer(model_name)
        self.embeddings = self.embedder.encode(documents, convert_to_tensor=False)

    def retrieve(self, query, top_k=5):
        query_vec = self.embedder.encode([query])
        sims = cosine_similarity(query_vec, self.embeddings)[0]
        indices = np.argsort(sims)[-top_k:][::-1]
        return [self.documents[i] for i in indices]

# Loại bỏ tag HTML
def remove_html_tags(text):
    return re.sub(r'<.*?>', '', text)

# Gọi Gemini API để sinh câu trả lời
def generate_answer(query, context_docs):
    context = "\n\n".join(context_docs)
    prompt = f"""Bạn là một trợ lý nấu ăn. Dưới đây là một số món ăn liên quan:

{context}

Người dùng hỏi: "{query}"
Hãy trả lời một cách rõ ràng, súc tích, dễ hiểu bằng tiếng Việt."""
    response = model.generate_content(prompt).text
    return remove_html_tags(response.strip())

# Hàm xử lý chính
def handle_query(user_input, retriever):
    user_input = user_input.strip()
    related_docs = retriever.retrieve(user_input, top_k=5)
    response = generate_answer(user_input, related_docs)
    return "rag", response
