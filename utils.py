import pandas as pd
import random
import re

# Các thẻ xử lý câu hỏi chi tiết
keytasks_tags = [
    "nguyên liệu", "sơ chế", "cách làm", "cách dùng", "mẹo nhỏ", "gợi ý"
]

# Từ khóa liên quan đến món ăn, nguyên liệu, hương vị, phương pháp
keywords = [
    "bò", "heo", "gà", "cá", "tôm", "mực", "cua", "đậu phụ", "nấm", "trứng", "bơ", "phô mai", "rau",
    "khoai tây", "mặn", "ngọt", "chua", "cay", "béo", "chua ngọt", "thanh mát", "chay", "hải sản",
    "thảo mộc", "bơ tỏi", "xào", "luộc", "hấp", "nướng", "chiên", "rang", "om", "hầm", "kho",
    "ngâm", "muối", "sấy", "quay", "áp chảo", "súp", "lẩu", "salad", "cuốn", "trộn", "sốt"
]

# Mapping tên thẻ tiếng Việt sang cột trong DataFrame
def tag_map(tag):
    return {
        "nguyên liệu": "ingredients",
        "sơ chế": "description",
        "cách làm": "steps",
        "cách dùng": "usage",
        "mẹo nhỏ": "tips"
    }.get(tag, tag)

# Hàm loại bỏ thẻ HTML như <b>, <br>
def remove_html_tags(text):
    return re.sub(r'<.*?>', '', text)

import pandas as pd
import random
import re

# Các thẻ xử lý câu hỏi chi tiết
keytasks_tags = [
    "nguyên liệu", "sơ chế", "cách làm", "cách dùng", "mẹo nhỏ", "gợi ý"
]

# Từ khóa liên quan đến món ăn, nguyên liệu, hương vị, phương pháp
keywords = [
    "bò", "heo", "gà", "cá", "tôm", "mực", "cua", "đậu phụ", "nấm", "trứng", "bơ", "phô mai", "rau",
    "khoai tây", "mặn", "ngọt", "chua", "cay", "béo", "chua ngọt", "thanh mát", "chay", "hải sản",
    "thảo mộc", "bơ tỏi", "xào", "luộc", "hấp", "nướng", "chiên", "rang", "om", "hầm", "kho",
    "ngâm", "muối", "sấy", "quay", "áp chảo", "súp", "lẩu", "salad", "cuốn", "trộn", "sốt"
]

# Mapping tên thẻ tiếng Việt sang cột trong DataFrame
def tag_map(tag):
    return {
        "nguyên liệu": "ingredients",
        "sơ chế": "description",
        "cách làm": "steps",
        "cách dùng": "usage",
        "mẹo nhỏ": "tips"
    }.get(tag, tag)

# Hàm loại bỏ thẻ HTML như <b>, <br>
def remove_html_tags(text):
    return re.sub(r'<.*?>', '', text)

# Trả kết quả Markdown đẹp từ 1 dòng dữ liệu
def format_recipe_markdown(row):
    title = f"🍽️ {row.get('title', '').strip()}"
    ingredients = f"📋 Nguyên liệu: {row.get('ingredients', '').strip()}"
    steps = f"👨‍🍳 Cách làm: {row.get('steps', '').strip()}"
    usage = f"🕒 Cách dùng: {row['usage'].strip()}" if pd.notna(row.get('usage')) else ""
    tips = f"💡 Mẹo nhỏ: {row['tips'].strip()}" if pd.notna(row.get('tips')) else ""

    combined = f"{title}<br><br>{ingredients}<br><br>{steps}<br><br>{usage}<br><br>{tips}"
    return remove_html_tags(combined)

# Xử lý truy vấn người dùng
def handle_query(user_input, df):
    user_input = user_input.lower().strip()

    # Gợi ý ngẫu nhiên
    if "gợi ý" in user_input and not any(kw in user_input for kw in keywords):
        samples = df.sample(5)
        markdown_list = [format_recipe_markdown(row) for _, row in samples.iterrows()]
        return "list", "\n\n---\n\n".join(markdown_list)

    # Gợi ý theo từ khóa
    elif "gợi ý" in user_input:
        filtered = df[df['title'].str.lower().apply(
            lambda title: any(kw in title for kw in keywords if kw in user_input)
        )]
        if filtered.empty:
            return "error", "❌ Không tìm thấy món phù hợp với từ khóa bạn đã nhập."
        samples = filtered.sample(min(5, len(filtered)))
        markdown_list = [format_recipe_markdown(row) for _, row in samples.iterrows()]
        return "list", "\n\n---\n\n".join(markdown_list)

    # Câu hỏi chi tiết như: nguyên liệu phở bò
    matched_tags = [tag for tag in keytasks_tags if tag in user_input and tag != "gợi ý"]
    if matched_tags:
        for tag in matched_tags:
            name_part = user_input.replace(tag, "").strip()
            filtered = df[df['title'].str.lower() == name_part]
            if not filtered.empty:
                row = filtered.iloc[0]
                content = row.get(tag_map(tag), "Không có thông tin.")
                response = f"🍽️ {row['title']}\n\n🔍 {tag.capitalize()}:\n{content.strip()}"
                return "detail", remove_html_tags(response)

    # Không khớp gì cả
    return "error", "❌ Không tìm thấy món ăn hoặc thông tin phù hợp với yêu cầu."


# Xử lý truy vấn người dùng
def handle_query(user_input, df):
    user_input = user_input.lower().strip()

    # Gợi ý ngẫu nhiên
    if "gợi ý" in user_input and not any(kw in user_input for kw in keywords):
        samples = df.sample(5)
        markdown_list = [format_recipe_markdown(row) for _, row in samples.iterrows()]
        return "list", "\n\n---\n\n".join(markdown_list)

    # Gợi ý theo từ khóa
    elif "gợi ý" in user_input:
        filtered = df[df['title'].str.lower().apply(
            lambda title: any(kw in title for kw in keywords if kw in user_input)
        )]
        if filtered.empty:
            return "error", "❌ Không tìm thấy món phù hợp với từ khóa bạn đã nhập."
        samples = filtered.sample(min(5, len(filtered)))
        markdown_list = [format_recipe_markdown(row) for _, row in samples.iterrows()]
        return "list", "\n\n---\n\n".join(markdown_list)

    # Câu hỏi chi tiết như: nguyên liệu phở bò
    matched_tags = [tag for tag in keytasks_tags if tag in user_input and tag != "gợi ý"]
    if matched_tags:
        for tag in matched_tags:
            name_part = user_input.replace(tag, "").strip()
            filtered = df[df['title'].str.lower() == name_part]
            if not filtered.empty:
                row = filtered.iloc[0]
                content = row.get(tag_map(tag), "Không có thông tin.")
                response = f"🍽️ {row['title']}\n\n🔍 {tag.capitalize()}:\n{content.strip()}"
                return "detail", remove_html_tags(response)

    # Không khớp gì cả
    return "error", "❌ Không tìm thấy món ăn hoặc thông tin phù hợp với yêu cầu."
