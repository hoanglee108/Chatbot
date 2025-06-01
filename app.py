import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from api import model  # Đảm bảo đã khởi tạo model Gemini ở đây

# Đọc dữ liệu món ăn
@st.cache_data
def load_data():
    return pd.read_csv("crawl/mon_ngon.csv")

# Vector hóa tiêu đề để tìm kiếm bằng từ khóa
@st.cache_resource
def get_vectorizer_and_matrix(titles):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(titles)
    return vectorizer, tfidf_matrix

# Prompt mẫu gửi cho Gemini
prompt_template = """
Hãy định dạng thông tin món ăn sau thành Markdown có biểu tượng emoji cho từng phần. Giữ nguyên các dòng bằng <br> nếu có.

Tiêu đề: {title}

Nguyên liệu:
{ingredients}

Cách làm:
{steps}

Cách dùng:
{usage}

Mẹo nhỏ:
{tips}
"""

# Gọi Gemini để định dạng món ăn
def format_recipe_with_model(row):
    prompt = prompt_template.format(
        title=row.get("title", ""),
        ingredients=row.get("ingredients", ""),
        steps=row.get("steps", ""),
        usage=row.get("usage", ""),
        tips=row.get("tips", "")
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Fallback nếu lỗi
        return fallback_format(row)

# Dự phòng: định dạng thủ công nếu Gemini lỗi
def fallback_format(row):
    text = f"""### 🍽️ {row['title']}

**📋 Nguyên liệu:**<br>
{row['ingredients']}

**👨‍🍳 Cách làm:**<br>
{row['steps']}
"""
    if 'usage' in row and pd.notna(row['usage']):
        text += f"<br><br>**🕒 Cách dùng:**<br>{row['usage']}"
    if 'tips' in row and pd.notna(row['tips']):
        text += f"<br><br>**💡 Mẹo nhỏ:**<br>{row['tips']}"
    return text

# Load dữ liệu và vector hóa
recipes_df = load_data()
vectorizer, tfidf_matrix = get_vectorizer_and_matrix(recipes_df['title'].fillna(""))

# Giao diện chính
st.title("🍜 Chatbot Món Ăn Đơn Giản")

# Lưu lịch sử chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_history = st.session_state.chat_history
user_input = st.chat_input("Hãy hỏi tôi về món ăn, ví dụ: 'Tôi muốn món cay', 'Phở bò', 'Nguyên liệu bánh xèo'")

# Nếu người dùng nhập tin nhắn mới
if user_input:
    chat_history.append(("Bạn", user_input))
    st.session_state.chat_history = chat_history

# Hiển thị toàn bộ lịch sử chat
for sender, message in chat_history:
    with st.chat_message("user" if sender == "Bạn" else "assistant"):
        st.markdown(message)


# Nếu có câu hỏi mới từ người dùng
if chat_history:
    last_user_msg = chat_history[-1][1]
    if last_user_msg:
        user_input_lower = last_user_msg.lower()
        with st.spinner("Đang xử lý..."):
            if "gợi ý" in user_input_lower:
                samples = recipes_df.sample(n=5)
                with st.chat_message("assistant"):
                    st.markdown("### Gợi ý 5 món ngẫu nhiên:")
                for _, row in samples.iterrows():
                    formatted = format_recipe_with_model(row)
                    with st.chat_message("assistant"):
                        st.markdown(formatted, unsafe_allow_html=True)
            else:
                query_vec = vectorizer.transform([last_user_msg])
                similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
                recipes_df["similarity"] = similarities
                top_matches = recipes_df.sort_values("similarity", ascending=False).head(5)
                with st.chat_message("assistant"):
                    st.markdown("### Các món gần với yêu cầu của bạn:")
                for _, row in top_matches.iterrows():
                    formatted = format_recipe_with_model(row)
                    st.markdown(formatted, unsafe_allow_html=True)
