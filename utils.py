import pandas as pd
import random

keytasks_tags = [
    "nguyên liệu", "sơ chế", "cách làm", "cách dùng", "mẹo nhỏ", "gợi ý"
]

keywords = [
    "bò", "heo", "gà", "cá", "tôm", "mực", "cua", 
    "đậu phụ", "nấm", "trứng", "bơ", "phô mai", "rau",
    "khoai tây", "mặn", "ngọt", "chua", "cay",   
    "béo", "chua ngọt", "thanh mát", "chay", "hải sản",
    "thảo mộc", "bơ tỏi", 
    "xào", "luộc", "hấp", "nướng", "chiên", "rang", "om", 
    "hầm", "kho", "ngâm", "muối", "sấy", "quay", "áp chảo",
    "súp", "lẩu", "salad", "cuốn", "trộn", "sốt"
]

def tag_map(tag):
    return {
        "nguyên liệu": "ingredients",
        "sơ chế": "description",
        "cách làm": "steps",
        "cách dùng": "usage",
        "mẹo nhỏ": "tips"
    }.get(tag, tag)

def handle_query(user_input, df):
    user_input = user_input.lower()

    # Gợi ý ngẫu nhiên
    if "gợi ý" in user_input and not any(kw in user_input for kw in keywords):
        results = df.sample(5)
        return "list", results

    # Gợi ý kèm keyword
    elif "gợi ý" in user_input:
        filtered = df[df['title'].str.lower().apply(
            lambda title: any(kw in title for kw in keywords if kw in user_input)
        )]
        results = filtered.sample(min(5, len(filtered))) if not filtered.empty else pd.DataFrame()
        return "list", results

    # Câu hỏi cụ thể
    else:
        matched_tags = [tag for tag in keytasks_tags if tag in user_input and tag != "gợi ý"]
        if matched_tags:
            for tag in matched_tags:
                name_part = user_input.replace(tag, "").strip()
                filtered = df[df['title'].str.lower() == name_part]
                if not filtered.empty:
                    row = filtered.iloc[0]
                    return "detail", {
                        "title": row['title'],
                        "tag": tag,
                        "content": row.get(tag_map(tag), "Không tìm thấy thông tin")
                    }
        return "error", "Không tìm thấy món ăn hoặc thông tin phù hợp."
