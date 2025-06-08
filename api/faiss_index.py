# import faiss
# import numpy as np
# from api.models import YouTubeVideo

# def build_faiss_index():
#     videos = YouTubeVideo.objects.filter(status="approved")
#     video_embeddings = []
#     video_ids = []

#     for video in videos:
#         content = f"{video.title}\n{video.description}"
#         embedding = get_embedding(content)
#         video_embeddings.append(embedding)
#         video_ids.append(video.id)

#     if not video_embeddings:
#         return None, []

#     dimension = len(video_embeddings[0])
#     index = faiss.IndexFlatL2(dimension)
#     index.add(np.array(video_embeddings, dtype=np.float32))
    
#     return index, video_ids



# yourapp/faiss_index.py
import numpy as np
import faiss
from api.models import YouTubeVideo
_index = None
_video_ids = []

def build_faiss_index():
    global _index, _video_ids
    if _index is not None:
        return _index, _video_ids

    vectors = []
    video_ids = []

    for video in YouTubeVideo.objects.exclude(embedding__isnull=True):
        vector = np.frombuffer(video.embedding, dtype=np.float32)
        vectors.append(vector)
        video_ids.append(video.id)

    if not vectors:
        return None, []

    vectors_np = np.vstack(vectors).astype("float32")
    _index = faiss.IndexFlatL2(vectors_np.shape[1])
    _index.add(vectors_np)
    _video_ids = video_ids

    return _index, _video_ids
