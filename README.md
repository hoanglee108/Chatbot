# 🧠 Chatbot Dựa Trên CLIP & Gemini

## 📌 Mục tiêu dự án

Xây dựng một ứng dụng trả lời câu hỏi thông minh kết hợp giữa:

- **CLIP**: Tìm kiếm câu hỏi gần giống nhất dựa trên ngữ nghĩa.
- **Gemini AI**: Sinh câu trả lời ngắn gọn, chính xác, dễ hiểu.
- **PDF trích xuất**: Tự động trích câu hỏi, đáp án, hình ảnh từ tài liệu gốc.
- **Thi thử**: Hỗ trợ tạo đề thi thử 30 câu từ bộ dữ liệu đã xử lý.

---

## 🧰 Công nghệ sử dụng

- `PyMuPDF (fitz)`: Trích xuất hình ảnh từ PDF.
- `pdfminer.six`: Phân tích văn bản và phát hiện underline trong đáp án.
- `transformers`: Sử dụng `CLIPModel` và `CLIPTokenizer`.
- `Streamlit`: Giao diện web đơn giản, tương tác.
- `Google Gemini`: Tối ưu hóa trả lời bằng ngôn ngữ tự nhiên.

---

## ⚙️ Quy trình hoạt động

1. **Trích xuất dữ liệu từ PDF**:
    - Câu hỏi, đáp án, đáp án đúng (gạch chân).
    - Hình ảnh minh họa từng trang.

2. **Ghi ra file `questions.csv`**:
    - Cột: ID, câu hỏi, đáp án đúng, các lựa chọn, ảnh minh họa.

3. **Giao diện người dùng** (`Streamlit`):
    - Nhập câu hỏi bất kỳ.
    - So sánh với dữ liệu bằng embedding CLIP.
    - Hiển thị kết quả gần đúng + hình ảnh + sinh trả lời từ Gemini.

4. **(Dự kiến)** Tạo đề thi thử gồm 30 câu ngẫu nhiên từ dữ liệu.

---

## 📁 Cấu trúc dự án
```
Chatbot
├── questions.csv # File chứa dữ liệu câu hỏi
├── images/ # Thư mục chứa ảnh minh họa
├── driving_data.pdf # File PDF gốc
├── extract_questions.py # Script trích xuất từ PDF
├── app.py # Ứng dụng Streamlit
└── api.py # Gọi Gemini API
```

---

## 🚀 Khởi chạy ứng dụng

```bash
streamlit run app.py
```

## 🧪 Tính năng dự kiến mở rộng

- [ ] **Thi thử 30 câu ngẫu nhiên**  
  Cho phép người dùng bắt đầu một bài thi gồm 30 câu hỏi được chọn ngẫu nhiên từ bộ dữ liệu. Hệ thống sẽ chấm điểm và hiển thị kết quả sau khi hoàn thành.

- [ ] **Lưu kết quả làm bài**  
  Ghi lại các lựa chọn của người dùng, đáp án đúng/sai, thời gian làm bài để đánh giá quá trình học tập.

- [ ] **Phân tích chủ đề và độ khó**  
  Gắn nhãn chủ đề và mức độ khó cho từng câu hỏi. Sau khi làm bài, thống kê kết quả theo từng nhóm để xác định điểm mạnh/yếu.

- [ ] **Cho phép upload tài liệu PDF mới**  
  Người dùng có thể tải lên file PDF mới chứa bộ câu hỏi riêng. Hệ thống sẽ tự động trích xuất và thêm vào cơ sở dữ liệu hiện có.
