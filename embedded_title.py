import pandas as pd
from transformers import CLIPProcessor, CLIPModel
import torch
import numpy as np
from tqdm import tqdm

df = pd.read_csv("crawl/mon_ngon.csv")

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

titles = df['title'].astype(str).tolist()

embeddings = []

for title in tqdm(titles, desc="Embedding titles"):
    inputs = processor(text=title, return_tensors="pt", padding=True, truncation=True).to(device)
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
    embeddings.append(text_features.cpu().numpy())

embeddings_np = np.vstack(embeddings) 


np.save("mon_ngon.npy", embeddings_np)
