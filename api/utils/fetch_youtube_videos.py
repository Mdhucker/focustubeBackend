import isodate
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.utils.dateparse import parse_datetime
from decouple import config
from api.models import YouTubeVideo, VideoCategory

# ✅ Define keywords per category
CATEGORY_KEYWORDS = {
    "Islamic": ["quran", "islam", "hadith", "muslim", "muhammad", "allah"],
    "Technology": ["ai", "tech", "software", "app", "robot", "device"],
    "Education": ["lecture", "study", "education", "learning", "class", "course"],
    "Business": ["market", "business", "startup", "entrepreneur", "company", "profit"],
    "Politics": ["president", "government", "trump", "biden", "minister", "election"],
    "Motivation": ["motivation", "success", "mindset", "discipline", "inspire", "positive thinking", "self-improvement", "goal setting", "overcome challenges", "ambition"],
    "Health": ["health", "fitness", "diet", "exercise", "mental", "wellness", "nutrition", "self-care", "mental health", "mindfulness"],
    "Sports": ["football", "soccer", "nba", "cricket", "match", "goal", "athletes", "team", "competition", "championship"],
    "Music": ["song", "music", "album", "artist", "track", "melody", "lyrics", "composer", "band", "concert"],
    "War": ["war", "conflict", "battle", "military", "combat", "soldiers", "peace", "fight", "violence", "conflict resolution"],
    "Poverty": ["poverty", "hunger", "homeless", "poverty alleviation", "social justice", "economic inequality", "underprivileged", "disadvantaged", "charity", "economic disparity"],
    "Children": ["children", "kids", "youth", "childcare", "education for children", "child development", "parenting", "family", "youth empowerment", "childhood education"],
    "Mindset": ["mindset", "positive thinking", "growth mindset", "mental strength", "mental toughness", "resilience", "perseverance", "self-discipline", "focus", "determination"],
}

def is_video_long_enough(duration_str):
    """Check if the video is at least 5 minutes long."""
    duration = isodate.parse_duration(duration_str)
    return duration.total_seconds() >= 300  # 5 minutes

def assign_category(title, description, youtube_category_id):
    """Assign category based on keywords in title and description, fallback to YouTube category."""
    text = f"{title} {description}".lower()
    
    # First try the custom categorization logic
    for category_name, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category_name
    
    # If custom categorization fails, use YouTube's category ID
    youtube_category_mapping = {
        "1": "Film & Animation",
        "2": "Autos & Vehicles",
        "10": "Music",
        "15": "Pets & Animals",
        "17": "Sports",
        "18": "Short Movies",
        "19": "Travel & Events",
        "20": "Gaming",
        "21": "Videoblogging",
        "22": "People & Blogs",
        "23": "Comedy",
        "24": "Entertainment",
        "25": "News & Politics",
        "26": "How-to & Style",
        "27": "Education",
        "28": "Science & Technology",
        "29": "Nonprofits & Activism",
        "30": "Movies",
        "31": "Animes",
        "32": "Action & Adventure",
        "33": "Classics",
        "34": "Documentary",
        "35": "Drama",
        "36": "Family",
        "37": "Foreign",
        "38": "Horror",
        "39": "Independent",
        "40": "Romance",
        "41": "Sci-Fi & Fantasy",
        "42": "Thriller",
        "43": "Mystery",
        "44": "Game Show",
        "45": "Reality",
        "46": "Soap Opera",
        "47": "Talk Show",
        "48": "Lifestyle",
        "49": "Vlog",
        "50": "Music Video",
        "51": "Live Music",
        "52": "Experimental",
        "53": "Electronic"
    }
    
    # Return the mapped YouTube category or "Uncategorized" if no match
    return youtube_category_mapping.get(youtube_category_id, "Uncategorized")

def fetch_videos(channel_id, max_results):
    """Fetch videos from a YouTube channel and categorize them."""
    api_key = config("api_key_youtube")
    if not api_key:
        raise ValueError("YouTube API key is missing. Please set 'api_key_youtube' in your environment variables.")

    youtube = build('youtube', 'v3', developerKey=api_key)
    search_request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        type='video',
        maxResults=max_results,
        order='date'
    )
    search_response = search_request.execute()

    print(f"Search response: {search_response}")

    count_saved = 0
    video_list = []

    for item in search_response.get('items', []):
        video_id = item['id']['videoId']
        snippet = item['snippet']
        youtube_category_id = snippet.get('categoryId', '')  # Get YouTube's category ID

        print(f"Processing video: {video_id} - {snippet['title']}")

        try:
            video_request = youtube.videos().list(part='contentDetails', id=video_id)
            video_response = video_request.execute()

            if not video_response.get('items'):
                print(f"No content details for video {video_id}")
                continue

            duration = video_response['items'][0]['contentDetails'].get('duration')
            if not duration:
                print(f"No duration info for video {video_id}")
                continue

            print(f"Video duration: {duration}")
            if not is_video_long_enough(duration):
                print(f"Skipping video {video_id} due to short duration")
                continue

        except HttpError as e:
            print(f"Error fetching details for video {video_id}: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error for video {video_id}: {e}")
            continue

        if YouTubeVideo.objects.filter(video_id=video_id).exists():
            print(f"Video {video_id} already exists.")
            continue

        # ✅ Assign category using both custom keywords and YouTube category ID
        category_name = assign_category(snippet['title'], snippet.get('description', ''), youtube_category_id)

        # Get or create the VideoCategory instance
        category_obj, _ = VideoCategory.objects.get_or_create(name=category_name)

        # Create video with assigned category
        video = YouTubeVideo.objects.create(
            video_id=video_id,
            title=snippet['title'],
            description=snippet.get('description', ''),
            thumbnail_url=snippet['thumbnails'].get('high', {}).get('url', ''),
            published_at=parse_datetime(snippet['publishedAt']),
            channel_title=snippet['channelTitle'],
            category=category_obj  # Correct category assignment
        )

        count_saved += 1
        video_list.append(snippet['title'])

    print(f"Saved {count_saved} videos.")
    return count_saved, video_list