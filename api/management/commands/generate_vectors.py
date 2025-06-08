# yourapp/management/commands/generate_vectors.py
from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from api.models import YouTubeVideo

class Command(BaseCommand):
    help = "Generate vector embeddings for all YouTube videos and store them"

    def handle(self, *args, **kwargs):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        videos = YouTubeVideo.objects.all()

        for video in videos:
            text = f"{video.title} {video.description}"
            embedding = model.encode([text])[0].astype(np.float32)

            # Save binary embedding to database
            video.embedding = embedding.tobytes()
            video.save()

        self.stdout.write(self.style.SUCCESS("Saved embeddings to database."))
