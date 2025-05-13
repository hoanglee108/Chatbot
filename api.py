import google.generativeai as genai

# Cấu hình API key
genai.configure(api_key="key")

# Khởi tạo model Gemini 1.5
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash",  # hoặc models/gemini-1.5-pro
)
