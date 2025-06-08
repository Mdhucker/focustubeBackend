import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from api.models import YouTubeVideo, VideoCategory
from api.utils.subcategory_examples import SUBCATEGORY_EXAMPLES

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384
index = faiss.IndexFlatL2(dimension)
subcategory_labels = []

# Step 1: Preload subcategory embeddings into FAISS index
def preload_subcategories_to_vector_db():
    global subcategory_labels
    subcategory_labels.clear()  # Clear old labels to avoid duplicates
    texts = []
    for label, examples in SUBCATEGORY_EXAMPLES.items():
        for example in examples:
            texts.append(example)
            subcategory_labels.append(label)
    vectors = model.encode(texts).astype("float32")
    index.reset()  # Clear any previous vectors in the index
    index.add(vectors)

# Step 2: Embed video title + description into vector
def get_video_embedding(title: str, description: str) -> np.ndarray:
    text = f"{title}. {description}"
    return model.encode(text).astype("float32").reshape(1, -1)

# Step 3: Find best matching subcategory by nearest neighbor search
def find_best_subcategory(embedding: np.ndarray, similarity_threshold=0.7) -> str:
    distances, indices = index.search(embedding, k=1)
    # distances are squared L2 distances; smaller is better
    # You may convert distance to similarity if you want, or just rely on minimal distance
    best_distance = distances[0][0]
    best_label = subcategory_labels[indices[0][0]]

    # Optional threshold: reject if distance too large (means low similarity)
    # You can experiment to find a good threshold
    if best_distance > 1.0:  # example threshold (adjust based on your tests)
        return "Uncategorized:Uncategorized"

    return best_label

# Step 4: Full video categorization logic
def categorize_video(video: YouTubeVideo):
    if index.ntotal == 0:
        preload_subcategories_to_vector_db()

    embedding = get_video_embedding(video.title, video.description)
    label = find_best_subcategory(embedding)
    category_name, subcategory_name = label.split(":")

    # Get or create category object
    category_obj, _ = VideoCategory.objects.get_or_create(name=category_name)

    video.category = category_obj
    video.subcategory = subcategory_name

    # Optionally store embedding (flattened list) in video, if you want
    video.embedding = embedding.flatten().tolist()

    video.save()
