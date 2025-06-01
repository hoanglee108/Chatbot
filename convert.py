import os
import csv
import re
import fitz

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

# ---------------- Trích câu hỏi và đáp án ----------------
def extract_questions_from_pdf_fitz(pdf_path):
    doc = fitz.open(pdf_path)
    results = []

    for page_num, page in enumerate(doc, start=1):
        text_dict = page.get_text("dict")
        current_question = None

        for block in text_dict["blocks"]:
            for line in block.get("lines", []):
                line_text = "".join([span["text"] for span in line["spans"]]).strip()

                # Tìm câu hỏi
                match_q = re.match(r"^Câu\s+(\d+)\.\s*(.+)", line_text)
                if match_q:
                    if current_question:
                        results.append(current_question)
                    current_question = {
                        "id": match_q.group(1),
                        "question": match_q.group(2),
                        "answers": [],
                        "page": page_num,
                        "images": []
                    }
                    continue

                # Tìm đáp án
                match_a = re.match(r"^(\d)\.\s*(.+)", line_text)
                if match_a and current_question:
                    index = match_a.group(1)
                    answer_text = match_a.group(2)
                    current_question["answers"].append(f"{index}. {answer_text}")

        if current_question:
            results.append(current_question)

    return results

# ---------------- Ghi ra CSV ----------------
def write_to_csv(questions, output_csv):
    with open(output_csv, "w", newline='', encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Câu hỏi", "Các lựa chọn", "Ảnh minh họa"])
        for q in questions:
            writer.writerow([
                q["id"],
                q["question"],
                "\n".join(q["answers"]),
                ", ".join(q.get("images", []))
            ])

# ---------------- Main ----------------
if __name__ == "__main__":
    print("📄 Đang trích xuất hình ảnh từ PDF...")
    image_map = extract_images_from_pdf(PDF_PATH, IMAGE_OUTPUT_DIR)

    print("🔍 Đang phân tích câu hỏi và đáp án...")
    questions = extract_questions_from_pdf_fitz(PDF_PATH)

    print("🖼️ Gán hình ảnh cho từng trang chứa câu hỏi...")
    for q in questions:
        q["images"] = image_map.get(q["page"], [])

    print("💾 Ghi ra CSV...")
    write_to_csv(questions, CSV_OUTPUT)

    print("✅ Xong! Dữ liệu lưu tại:", CSV_OUTPUT)
