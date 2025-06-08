# api/utils/subcategory_matcher.py

from sentence_transformers import SentenceTransformer, util
from .subcategory_examples import SUBCATEGORY_EXAMPLES

model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and fast

# Precompute example embeddings
subcategory_embeddings = {
    key: model.encode(examples, convert_to_tensor=True)
    for key, examples in SUBCATEGORY_EXAMPLES.items()
}

def match_subcategory(title, description):
    content = f"{title} {description}"
    video_embedding = model.encode(content, convert_to_tensor=True)

    best_score = -1
    best_match = "Uncategorized:Uncategorized"

    for subcat_key, example_embeddings in subcategory_embeddings.items():
        similarity = util.cos_sim(video_embedding, example_embeddings).max().item()
        if similarity > best_score:
            best_score = similarity
            best_match = subcat_key

    return best_match.split(":")  # Returns [main_category, subcategory]
