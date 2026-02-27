import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Load AI components
print("🚀 Loading AI Brain (174k rows)...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
index = faiss.read_index("farming.index")

with open("answers_list.pkl", "rb") as f:
    answers_list = pickle.load(f)

def get_intent_and_solution(english_query):
    """Finds the best solution in milliseconds"""
    query_vector = model.encode([english_query])
    D, I = index.search(query_vector, k=1)
    
    best_match_idx = I[0][0]
    return "Farming_Query", answers_list[best_match_idx]