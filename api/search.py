# api/search.py

from sentence_transformers import SentenceTransformer
from .faiss_index import build_faiss_index
from api.models import YouTubeVideo  # or from .models if in same dir

def search_similar_videos(query, k=6):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    index, video_ids = build_faiss_index()
    if index is None:
        return []

    query_vec = model.encode([query]).astype("float32")
    D, I = index.search(query_vec, k)

    results = []
    for idx in I[0]:
        if idx < len(video_ids):
            video = YouTubeVideo.objects.get(id=video_ids[idx])
            results.append(video)
    return results
