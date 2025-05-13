import streamlit as st
import pandas as pd
import torch
from transformers import CLIPTokenizer, CLIPModel
from api import model  # Đã cấu hình Gemini từ trước

# Load CLIP model
@st.cache_resource
def load_clip_model():
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")
    return model, tokenizer

clip_model, tokenizer = load_clip_model()

# Load câu hỏi từ CSV
@st.cache_data
def load_questions(csv_path="questions.csv"):
    return pd.read_csv(csv_path)

df = load_questions()

# Hàm tính embedding
def get_text_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = clip_model.get_text_features(**inputs)
    return outputs.squeeze()

# Streamlit UI
st.title("🔍 Ứng dụng Trợ lý câu hỏi (CLIP + Gemini)")
st.write("Nhập một câu hỏi bất kỳ. Hệ thống sẽ tìm câu gần giống nhất trong dữ liệu và đưa ra đáp án tối ưu.")

user_question = st.text_area("✏️ Nhập câu hỏi", "")

if st.button("Tìm và Tối ưu câu trả lời") and user_question.strip():
    with st.spinner("🔍 Đang tìm kiếm và xử lý..."):
        user_embedding = get_text_embedding(user_question)

        similarities = []
        for q in df["Câu hỏi"]:
            q_embed = get_text_embedding(q)
            sim = torch.nn.functional.cosine_similarity(user_embedding, q_embed, dim=0).item()
            similarities.append(sim)

        best_index = similarities.index(max(similarities))
        matched_row = df.iloc[best_index]

        best_question = matched_row["Câu hỏi"]
        correct_answer = matched_row["Đáp án đúng"]
        options = matched_row.get("Các lựa chọn", None)
        image = matched_row.get("Ảnh minh họa", None)

        st.subheader("✅ Câu hỏi tương tự nhất trong dữ liệu:")
        st.write(best_question)

        if options:
            st.subheader("📋 Các lựa chọn:")
            for opt in str(options).split("\n"):
                st.markdown(f"- {opt.strip()}")

        st.subheader("✔️ Đáp án đúng:")
        st.markdown(f"**{correct_answer}**")

        if isinstance(image, str) and image.strip():
            try:
                st.image(image.strip(), caption="Ảnh minh họa", use_column_width=True)
            except:
                st.warning("⚠️ Không thể tải ảnh minh họa.")

        # Tối ưu với Gemini
        gemini_prompt = f"""Câu hỏi người dùng: {user_question}
Câu hỏi tương tự trong dữ liệu: {best_question}
Đáp án đúng: {correct_answer}
Hãy đưa ra một câu trả lời ngắn gọn, chính xác và dễ hiểu."""

        gemini_response = model.generate_content(gemini_prompt)
        st.subheader("🤖 Trả lời từ Gemini:")
        st.write(gemini_response.text)
