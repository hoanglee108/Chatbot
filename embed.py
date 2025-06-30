import pandas as pd

def load_data(csv_path="mon_ngon.csv"):
    df = pd.read_csv(csv_path)
    df = df.fillna('')
    return df

from sentence_transformers import SentenceTransformer
import numpy as np

def create_embeddings(df, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
    model = SentenceTransformer(model_name)
    contents = (
        df['title'] + '. ' + 
        df['description'] + '. ' + 
        df['ingredients'] + '. ' +
        df['steps'] + '. ' + 
        df['usage'] + '. ' + 
        df['tips']
    ).tolist()
    embeddings = model.encode(contents, convert_to_tensor=False, show_progress_bar=True)
    return contents, np.array(embeddings)
