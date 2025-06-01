import google.generativeai as genai

# Cấu hình API key
genai.configure(api_key="AIzaSyBdaHu3dC4cG36SGiSuHTTFe-33hmaYof8")

# Khởi tạo model Gemini 1.5
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash",  # hoặc models/gemini-1.5-pro
)
