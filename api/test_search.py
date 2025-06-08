import os
import sys
import django

# Add root and project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'focustubeBase.settings')
django.setup()

from api.search import search_similar_videos  # change 'api' to your actual app name

# Run test
results = search_similar_videos("learn python programming", k=3)
for r in results:
    print(f"{r.title} - {r.description}")
