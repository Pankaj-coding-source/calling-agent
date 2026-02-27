import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os

# 1. Load the CSV
print("Reading 146k lines... Please wait.")
df = pd.read_csv("kcc_transcripts.csv") # <--- MAKE SURE FILENAME IS CORRECT

# 2. Clean data
df = df.dropna(subset=['questions', 'answers']) 

# 3. Load Multilingual Model (Supports Hindi, Odia, English)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("Generating Brain (Vector Index)... This will take time.")
questions = df['questions'].astype(str).tolist()
answers = df['answers'].astype(str).tolist()

# 4. Create Embeddings
embeddings = model.encode(questions, show_progress_bar=True, batch_size=32)

# 5. Build FAISS Index (Fast Search)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# 6. Save Files
faiss.write_index(index, "farming.index")
with open("answers.pkl", "wb") as f:
    pickle.dump(answers, f)

print("✅ Success! 'farming.index' and 'answers.pkl' created. Now run app.py")