import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from api import model

@st.cache_data
def load_data():
    return pd.read_csv("crawl/mon_ngon.csv")

@st.cache_resource
def get_vectorizer_and_matrix(titles):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(titles)
    return vectorizer, tfidf_matrix

recipes_df = load_data()
vectorizer, tfidf_matrix = get_vectorizer_and_matrix(recipes_df['title'].fillna(""))

st.title("🍜 Chatbot Món Ăn Đơn Giản")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_history = st.session_state.chat_history
user_input = st.chat_input("Hãy hỏi tôi về món ăn, ví dụ: 'Tôi muốn món cay', 'Phở bò', 'Nguyên liệu bánh xèo'")

def format_recipe_message(row):
    text = f"""### 🍽️ {row['title']}

**📋 Nguyên liệu:**  
{row['ingredients']}

**👨‍🍳 Cách làm:**  
{row['steps']}
"""
    if 'usage' in row and pd.notna(row['usage']):
        text += f"\n**🕒 Cách dùng:**\n{row['usage']}"
    if 'tips' in row and pd.notna(row['tips']):
        text += f"\n**💡 Mẹo nhỏ:**\n{row['tips']}"
    return text

# Khi user nhập
if user_input:
    chat_history.append(("Bạn", user_input))
    st.session_state.chat_history = chat_history

# Hiển thị toàn bộ chat
for sender, message in chat_history:
    if sender == "Bạn":
        with st.chat_message("user"):  # user message bên phải
            st.markdown(message)

# Hiển thị phần trả lời bot
if chat_history:
    last_user_msg = chat_history[-1][1]
    if last_user_msg:
        user_input_lower = last_user_msg.lower()
        with st.spinner("Đang xử lý..."):
            if "gợi ý" in user_input_lower:
                samples = recipes_df.sample(n=5)
                with st.chat_message("assistant"):  # bot message bên trái
                    st.markdown("### Gợi ý 5 món ngẫu nhiên:")
                for _, row in samples.iterrows():
                    with st.chat_message("assistant"):
                        st.markdown(format_recipe_message(row))
            else:
                query_vec = vectorizer.transform([last_user_msg])
                similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
                recipes_df["similarity"] = similarities
                top_matches = recipes_df.sort_values("similarity", ascending=False).head(5)
                with st.chat_message("assistant"):
                    st.markdown("### Các món gần với yêu cầu của bạn:")
                for _, row in top_matches.iterrows():
                        st.markdown(format_recipe_message(row))
