import pickle
from sentence_transformers import SentenceTransformer
import faiss
import sys

file_path = "english_farmer_model.pkl"

print(f"📂 Opening {file_path}...")
with open(file_path, "rb") as f:
    data = pickle.load(f)

# Extracting from the keys we found in check_pkl.py
questions = data.get('questions', [])
answers = data.get('answers', [])

if not questions or not answers:
    print("❌ Error: Could not find questions or answers in the dictionary.")
    sys.exit()

print(f"✅ Success! Found {len(questions)} rows of data.")

# --- Start AI Processing ---
print("🚀 Loading Multilingual AI Model...")
# This model is great for English, Hindi, and Odia
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("🧠 Generating Brain (Embeddings)... This will take ~20 mins for 146k lines.")
print("The AI is learning the relationship between all questions...")

# We convert questions into high-dimensional vectors
embeddings = model.encode(questions, show_progress_bar=True, batch_size=32)

print("💾 Creating and Saving the FAISS Index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Save the index (the brain)
faiss.write_index(index, "farming.index")

# Save the answers separately for quick lookup
with open("answers_list.pkl", "wb") as f:
    pickle.dump(answers, f)

print("\n✨ ALL DONE! PREPARATION COMPLETE.")
print("1. 'farming.index' created.")
print("2. 'answers_list.pkl' created.")
print("Now you can run 'app.py' to start the assistant.")