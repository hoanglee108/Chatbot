import os
import csv
import re
import fitz  # PyMuPDF
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

PDF_PATH = "driving_data.pdf"
CSV_OUTPUT = "questions.csv"
IMAGE_OUTPUT_DIR = "images"

# ---------------- Trích hình ảnh từ mỗi trang ----------------
def extract_images_from_pdf(pdf_path, output_dir="images"):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_map = {}

    for i, page in enumerate(doc):
        images = page.get_images(full=True)
        page_images = []
        for j, img in enumerate(images):
            base_image = doc.extract_image(img[0])
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"{output_dir}/page_{i+1}_img_{j+1}.{image_ext}"
            with open(image_filename, "wb") as f:
                f.write(image_bytes)
            page_images.append(image_filename)
        image_map[i + 1] = page_images
    return image_map

# ---------------- Trích câu hỏi, đáp án và đáp án đúng (underline) ----------------
def extract_questions_from_pdf(pdf_path):
    results = []
    current_question = None
    page_number = 0
    page_question_map = []

    for page_layout in extract_pages(pdf_path):
        page_number += 1
        for element in page_layout:
            if not isinstance(element, LTTextContainer):
                continue
            for text_line in element:
                if not isinstance(text_line, LTTextLine):
                    continue

                text = text_line.get_text().strip()

                # Tìm bắt đầu câu hỏi
                question_match = re.match(r"^Câu\s+(\d+)\.\s*(.+)", text)
                if question_match:
                    if current_question:
                        results.append(current_question)
                        page_question_map.append(page_number)

                    current_question = {
                        "id": question_match.group(1),
                        "question": question_match.group(2),
                        "answers": [],
                        "correct": "",
                        "page": page_number,
                        "images": []
                    }
                    continue

                # Tìm đáp án
                answer_match = re.match(r"^(\d)\.\s*(.+)", text)
                if answer_match and current_question:
                    index = answer_match.group(1)
                    answer_text = answer_match.group(2)
                    is_underlined = False

                    for char in text_line:
                        if isinstance(char, LTChar) and char.fontname:
                            if "underline" in char.fontname.lower():
                                is_underlined = True
                                break
                            # Có thể kiểm tra thêm font flags (nâng cao hơn)

                    if is_underlined:
                        current_question["correct"] = index

                    current_question["answers"].append(f"{index}. {answer_text}")

    if current_question:
        results.append(current_question)
        page_question_map.append(page_number)

    return results

# ---------------- Ghi ra CSV ----------------
def write_to_csv(questions, output_csv):
    with open(output_csv, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Câu hỏi", "Đáp án đúng", "Các lựa chọn", "Ảnh minh họa"])
        for q in questions:
            writer.writerow([
                q["id"],
                q["question"],
                q["correct"],
                "\n".join(q["answers"]),
                ", ".join(q.get("images", []))
            ])

# ---------------- Main ----------------
if __name__ == "__main__":
    print("📄 Đang trích xuất hình ảnh từ PDF...")
    image_map = extract_images_from_pdf(PDF_PATH, IMAGE_OUTPUT_DIR)

    print("🔍 Đang phân tích câu hỏi và đáp án underline...")
    questions = extract_questions_from_pdf(PDF_PATH)

    print("🖼️ Gán hình ảnh cho từng trang chứa câu hỏi...")
    for q in questions:
        q["images"] = image_map.get(q["page"], [])

    print("💾 Ghi ra CSV...")
    write_to_csv(questions, CSV_OUTPUT)

    print("✅ Xong! Dữ liệu lưu tại:", CSV_OUTPUT)
