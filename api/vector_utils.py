from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
import pickle
import hashlib

# === Load SentenceTransformer Model once ===
model = SentenceTransformer("all-MiniLM-L6-v2")

# === Constants ===
VECTOR_DIM = 384
INDEX_FILE = "vector_index.faiss"
META_FILE = "vector_metadata.pkl"

# === Load or initialize FAISS index ===
if os.path.exists(INDEX_FILE):
    index = faiss.read_index(INDEX_FILE)
else:
    base_index = faiss.IndexFlatL2(VECTOR_DIM)
    index = faiss.IndexIDMap(base_index)

# === Load or initialize metadata dictionary ===
if os.path.exists(META_FILE):
    with open(META_FILE, 'rb') as f:
        id_to_meta = pickle.load(f)
else:
    id_to_meta = {}

# === Embedding function ===
def get_embedding(text):
    if not text or not text.strip():
        return None
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding

# === Generate stable numeric ID from video_id string ===
def generate_stable_numeric_id(video_id):
    return int(hashlib.sha256(video_id.encode()).hexdigest(), 16) % (10**12)

# === Save embedding + metadata to FAISS index and disk ===
def save_embedding_to_faiss(video_id, embedding, metadata):
    global index, id_to_meta

    if embedding is None:
        raise ValueError("Embedding cannot be None.")

    embedding = np.array([embedding], dtype=np.float32)
    numeric_id = generate_stable_numeric_id(video_id)

    # Remove old entry if exists
    if numeric_id in id_to_meta:
        index.remove_ids(np.array([numeric_id], dtype=np.int64))

    # Add new embedding and metadata
    index.add_with_ids(embedding, np.array([numeric_id], dtype=np.int64))
    id_to_meta[numeric_id] = {'video_id': video_id, **metadata}

    # Persist index and metadata
    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, 'wb') as f:
        pickle.dump(id_to_meta, f)

# === Search FAISS index for similar embeddings ===
def vector_search(query_embedding, top_k=5):
    if query_embedding is None:
        raise ValueError("Query embedding cannot be None.")
        
    query_embedding = np.array([query_embedding], dtype=np.float32)
    distances, indices = index.search(query_embedding, top_k)
    results = []
    for i in range(top_k):
        faiss_id = int(indices[0][i])
        if faiss_id in id_to_meta:
            results.append({
                'video_id': id_to_meta[faiss_id]['video_id'],
                'metadata': id_to_meta[faiss_id],
                'distance': float(distances[0][i])
            })
    return results
