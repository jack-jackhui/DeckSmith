from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.IndexFlatL2(384)
texts = []  # To store texts with their corresponding vector indices

def add_to_vector_db(text):
    embeddings = model.encode([text])
    index.add(np.array(embeddings))
    texts.append(text)
    print(f"Added text to vector DB. Total texts: {len(texts)}")


def search_vector_db(query):
    if len(texts) == 0:
        print("Vector DB is empty. Returning no results.")
        return []

    query_embedding = model.encode([query])
    D, I = index.search(np.array(query_embedding), k=5)
    print(f"Query embedding: {query_embedding}")
    print(f"Distances: {D}")
    print(f"Indices: {I}")

    # Check if no results were found
    if I.size == 0 or len(I[0]) == 0:
        print("No results found in vector DB.")
        return []

    # Ensure indices are within range
    valid_indices = [i for i in I[0] if i < len(texts)]
    print(f"Valid indices: {valid_indices}")
    if not valid_indices:
        print("No valid indices found.")
        return []
    return [texts[i] for i in valid_indices]