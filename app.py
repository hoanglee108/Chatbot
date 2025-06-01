import streamlit as st
import pandas as pd
import torch
from transformers import CLIPProcessor, CLIPModel
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Chatbot Món Ăn", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("crawl/mon_ngon.csv")

@st.cache_resource
def load_clip_model():
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return model, processor

@st.cache_data
def embed_titles(titles):
    model, processor = load_clip_model()
    inputs = processor(text=titles, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        text_embeddings = model.get_text_features(**inputs)
    text_embeddings = text_embeddings / text_embeddings.norm(dim=-1, keepdim=True)  # Normalize
    return text_embeddings.cpu().numpy()

recipes_df = load_data()
model, processor = load_clip_model()
title_embeddings = embed_titles(recipes_df['title'].tolist())

st.title("🍜 Chatbot Món Ăn Thông Minh")

# Khởi tạo lịch sử chat nếu chưa có
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_history = st.session_state.chat_history
user_input = st.chat_input("Hãy hỏi tôi về món ăn, ví dụ: 'Tôi muốn món cay', 'Phở bò', 'Nguyên liệu bánh xèo'")

KEYWORDS = [
    "cay", "chay", "heo", "ngọt", "súp", "bánh", "cá", "bò", "gà", "tôm",
    "trứng", "rau", "cháo", "chè", "chiên", "hấp", "xào", "nướng", "kho"
]

if user_input:
    chat_history.append(("Bạn", user_input))
    with st.spinner("Đang xử lý..."):
        user_input_lower = user_input.lower()
        response = ""
        contains_keyword = any(kw in user_input_lower for kw in KEYWORDS)

        if "gợi ý" in user_input_lower:
            # Trường hợp 1: Gợi ý ngẫu nhiên
            sampled = recipes_df.sample(n=min(5, len(recipes_df)))
            response = "### Gợi ý món ngẫu nhiên cho bạn:\n"
            for _, row in sampled.iterrows():
                response += f"**{row['title']}**\n- {row['ingredients']}\n- {row['steps']}\n\n"

        elif contains_keyword:
            # Trường hợp 2: Dò bằng CLIP
            titles = recipes_df['title'].astype(str).tolist()
            title_embeddings = model.encode(titles, convert_to_tensor=True)
            query_embedding = model.encode(user_input, convert_to_tensor=True)

            cosine_scores = util.cos_sim(query_embedding, title_embeddings)[0]
            top_results = torch.topk(cosine_scores, k=min(5, len(recipes_df)))

            response = "### Các món phù hợp nhất:\n"
            for idx in top_results.indices:
                row = recipes_df.iloc[int(idx)]
                response += f"**{row['title']}**\n- {row['ingredients']}\n- {row['steps']}\n\n"

        else:
            response = "Bạn có thể thêm một vài từ khóa món ăn hoặc thử lại với câu hỏi khác."

    chat_history.append(("Bot", response))
    st.session_state.chat_history = chat_history


# Hiển thị lịch sử chat
for sender, message in chat_history:
    with st.chat_message(sender):
        st.markdown(message)
