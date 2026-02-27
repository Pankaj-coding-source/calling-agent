import pickle
import pandas as pd

file_path = "english_farmer_model.pkl"

with open(file_path, "rb") as f:
    data = pickle.load(f)

print("--- DEBUG INFO ---")
print(f"Type of data: {type(data)}")

if isinstance(data, pd.DataFrame):
    print("Columns found:", data.columns.tolist())
    print("First row:\n", data.head(1))
elif isinstance(data, list):
    print(f"Length of list: {len(data)}")
    print("First item type:", type(data[0]))
    print("First item content:", data[0])
elif isinstance(data, dict):
    print("Keys found:", data.keys())
else:
    print("Data content (first 200 chars):", str(data)[:200])