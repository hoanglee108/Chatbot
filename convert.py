import pandas as pd
import json

# Đọc file JSON
with open('crawl/mon_ngon.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Nếu JSON là danh sách các dicts (records), thì load trực tiếp
df = pd.DataFrame(data)

# Ghi ra CSV, giữ nguyên \n
df.to_csv('crawl/mon_ngon.csv', index=False, line_terminator='\n')
