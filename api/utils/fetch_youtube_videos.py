import os
import isodate
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.utils.dateparse import parse_datetime
from decouple import config

from api.models import YouTubeVideo, VideoCategory, VideoSubCategory
from .fetch_videos_function import fetch_videos
from .subcategory_examples import SUBCATEGORY_EXAMPLES
from ..vector_utils import get_embedding, vector_search
from .categorize_video import categorize_video  # ✅ LLaMA/vector categorization import

api_key_youtube = config("api_key_youtube")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_youtube_client():
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key_youtube)

def fetch_videos_by_keywords(youtube, keyword, max_results=10):
    return youtube.search().list(
        q=keyword,
        part="snippet",
        maxResults=min(max_results, 10),
        type="video",
        relevanceLanguage="en",
        safeSearch="moderate",
        order="date"
    ).execute()

def get_video_details(youtube, video_id):
    try:
        video_response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        ).execute()
        return video_response["items"][0] if video_response["items"] else None
    except Exception as e:
        print(f"❌ Error fetching details for video {video_id}: {e}")
        return None

def is_video_long_enough(duration_iso, min_seconds=60):
    try:
        duration = isodate.parse_duration(duration_iso).total_seconds()
        return duration >= min_seconds
    except Exception as e:
        print(f"❌ Error parsing video duration: {e}")
        return False

def find_matching_category_subcategory(title, description):
    combined_text = f"{title} {description}".lower()
    for full_subcat, keywords in SUBCATEGORY_EXAMPLES.items():
        for keyword in keywords:
            if keyword.lower() in combined_text:
                try:
                    category_name, subcategory_name = full_subcat.split(":")
                    return category_name.strip(), subcategory_name.strip()
                except ValueError:
                    continue
    return None, None

def fetch_videos_from_channel(channel_id, max_results=50):
    youtube = get_youtube_client()

    try:
        search_response = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            type='video',
            order='date',
            maxResults=min(max_results, 50)
        ).execute()
    except HttpError as e:
        print(f"❌ YouTube API Error: {e}")
        return 0, []
    except Exception as e:
        print(f"❌ Unexpected error while fetching videos: {e}")
        return 0, []

    saved = 0
    titles = []

    for item in search_response.get('items', []):
        try:
            video_id = item['id']['videoId']
            snippet = item['snippet']
            title = snippet['title']
            description = snippet.get('description', '')

            print(f"🔍 Checking video: {video_id} - {title}")

            details = youtube.videos().list(part='contentDetails,statistics', id=video_id).execute()
            if not details['items']:
                continue

            content_info = details['items'][0]['contentDetails']
            stats = details['items'][0]['statistics']
            duration = content_info['duration']

            if not is_video_long_enough(duration):
                print(f"⏭️ Skipping short video: {duration}")
                continue

            if YouTubeVideo.objects.filter(video_id=video_id).exists():
                print(f"⚠️ Video already exists: {video_id}")
                continue

            # Try keyword-based categorization
            category_name, subcategory_name = find_matching_category_subcategory(title, description)

            # If not found, fallback to LLaMA/vector model
            if not category_name or not subcategory_name:
                print(f"🤖 Calling LLaMA to categorize: {title}")
                cat_result = categorize_video(title, description)  # ✅ Now correctly passing 2 args
                if cat_result:
                    category_name = cat_result.get("category")
                    subcategory_name = cat_result.get("subcategory")
                if not category_name or not subcategory_name:
                    print(f"⏭️ Vector DB could not categorize video: {title}")
                    continue

            category_obj, _ = VideoCategory.objects.get_or_create(name=category_name)
            subcategory_obj, _ = VideoSubCategory.objects.get_or_create(
                name=subcategory_name,
                category=category_obj,
            )

            view_count = int(stats.get("viewCount", 0))
            like_count = int(stats.get("likeCount", 0))
            comment_count = int(stats.get("commentCount", 0))

            video = YouTubeVideo.objects.create(
                video_id=video_id,
                title=title,
                description=description,
                thumbnail_url=snippet['thumbnails'].get('high', {}).get('url', ''),
                published_at=parse_datetime(snippet['publishedAt']),
                channel_title=snippet['channelTitle'],
                duration=duration,
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                category=category_obj,
            )

            video.subcategory = subcategory_obj
            video.save()

            saved += 1
            titles.append(title)
            print(f"✅ Saved: {title}")

        except Exception as e:
            print(f"❌ Error processing video {video_id}: {e}")
            continue

    print(f"✅ Fetched and saved {saved} videos.")
    return saved, titles 

def get_channel_id_from_video_id(video_id: str) -> str:
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key_youtube}'
    try:
        response = requests.get(url)
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            return data['items'][0]['snippet']['channelId']
    except Exception as e:
        print(f"❌ Error getting channel ID for video {video_id}: {e}")
    return None


# import os
# import isodate
# import requests
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from django.utils.dateparse import parse_datetime
# from decouple import config
# from django.utils.text import slugify

# from api.models import YouTubeVideo, VideoCategory, VideoSubCategory
# from .category_keywords import CATEGORY_KEYWORDS
# from .fetch_videos_function import fetch_videos
# from .subcategory_matcher import match_subcategory  # ✅ Make sure this exists

# # Load API key
# api_key_youtube = config("api_key_youtube")
# YOUTUBE_API_SERVICE_NAME = "youtube"
# YOUTUBE_API_VERSION = "v3"

# def get_youtube_client():
#     return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key_youtube)

# def fetch_videos_by_keywords(youtube, keyword, max_results=10):
#     return youtube.search().list(
#         q=keyword,
#         part="snippet",
#         maxResults=min(max_results, 10),
#         type="video",
#         relevanceLanguage="en",
#         safeSearch="moderate",
#         order="date"
#     ).execute()

# def get_video_details(youtube, video_id):
#     try:
#         video_response = youtube.videos().list(
#             part="snippet,contentDetails,statistics",
#             id=video_id
#         ).execute()
#         return video_response["items"][0] if video_response["items"] else None
#     except Exception as e:
#         print(f"❌ Error fetching details for video {video_id}: {e}")
#         return None

# def is_video_long_enough(duration_iso, min_seconds=60):
#     try:
#         duration = isodate.parse_duration(duration_iso).total_seconds()
#         return duration >= min_seconds
#     except Exception as e:
#         print(f"❌ Error parsing video duration: {e}")
#         return False

# def assign_category(title, description, youtube_category_id=None):
#     """Simple keyword-based category and subcategory matching."""
#     text = f"{title} {description}".lower()
#     for category_name, keywords in CATEGORY_KEYWORDS.items():
#         for keyword in keywords:
#             if keyword.lower() in text:
#                 return category_name, keyword.title()
#     return "Uncategorized", None

# def fetch_and_save_videos(channel_id=None, max_results=10):
#     youtube = get_youtube_client()
#     total_saved = 0
#     saved_titles = []

#     for category_name, keywords in CATEGORY_KEYWORDS.items():
#         if total_saved >= max_results:
#             break

#         category_obj, _ = VideoCategory.objects.get_or_create(name=category_name)

#         for keyword in keywords:
#             if total_saved >= max_results:
#                 break

#             try:
#                 search_results = fetch_videos_by_keywords(youtube, keyword, max_results=10)

#                 for item in search_results.get("items", []):
#                     if total_saved >= max_results:
#                         break

#                     video_id = item["id"]["videoId"]
#                     snippet = item["snippet"]

#                     if YouTubeVideo.objects.filter(video_id=video_id).exists():
#                         continue

#                     details = get_video_details(youtube, video_id)
#                     if not details:
#                         continue

#                     duration = details["contentDetails"]["duration"]
#                     if not is_video_long_enough(duration):
#                         print(f"⏭️ Skipping short video: {video_id}")
#                         continue

#                     stats = details.get("statistics", {})
#                     view_count = int(stats.get("viewCount", 0))
#                     like_count = int(stats.get("likeCount", 0))
#                     comment_count = int(stats.get("commentCount", 0))

#                     # Match subcategory
#                     subcategory = match_subcategory(snippet["title"], snippet.get("description", ""))
#                     subcategory_objs = []

#                     for subcat_name in subcategory:
#                         subcat_obj, _ = VideoSubCategory.objects.get_or_create(
#                             name=subcat_name,
#                             category=category_obj,
#                             defaults={"slug": slugify(subcat_name)}
#                         )
#                         subcategory_objs.append(subcat_obj)

#                     video = YouTubeVideo.objects.create(
#                         video_id=video_id,
#                         title=snippet["title"],
#                         description=snippet.get("description", ""),
#                         published_at=parse_datetime(snippet["publishedAt"]),
#                         thumbnail_url=snippet["thumbnails"]["high"]["url"],
#                         channel_title=snippet["channelTitle"],
#                         duration=duration,
#                         view_count=view_count,
#                         like_count=like_count,
#                         comment_count=comment_count,
#                         category=category_obj,
#                     )

#                     video.subcategory.set(subcategory_objs)

#                     print(f"✅ Saved: {video.title} ({category_name})")
#                     total_saved += 1
#                     saved_titles.append(video.title)

#             except HttpError as e:
#                 print(f"❌ YouTube API error: {e}")
#             except Exception as e:
#                 print(f"❌ Error processing keyword '{keyword}': {e}")

#     return total_saved, saved_titles


# def fetch_videos_from_channel(channel_id, max_results=50):
#     youtube = get_youtube_client()

#     try:
#         search_response = youtube.search().list(
#             part='snippet',
#             channelId=channel_id,
#             type='video',
#             order='date',
#             maxResults=min(max_results, 50)
#         ).execute()
#     except HttpError as e:
#         print(f"❌ YouTube API Error: {e}")
#         return 0, []
#     except Exception as e:
#         print(f"❌ Unexpected error while fetching videos: {e}")
#         return 0, []

#     saved = 0
#     titles = []

#     for item in search_response.get('items', []):
#         try:
#             video_id = item['id']['videoId']
#             snippet = item['snippet']
#             title = snippet['title']
#             description = snippet.get('description', '')

#             print(f"🔍 Checking video: {video_id} - {title}")

#             details = youtube.videos().list(part='contentDetails,statistics', id=video_id).execute()
#             content_info = details['items'][0]['contentDetails']
#             stats = details['items'][0]['statistics']
#             duration = content_info['duration']

#             if not is_video_long_enough(duration):
#                 print(f"⏭️ Skipping short video: {duration}")
#                 continue

#             if YouTubeVideo.objects.filter(video_id=video_id).exists():
#                 print(f"⚠️ Video already exists: {video_id}")
#                 continue

#             category_name, subcategory_name = assign_category(title, description)
#             category_obj, _ = VideoCategory.objects.get_or_create(name=category_name)

#             subcategory_obj = None
#             if subcategory_name:
#                 subcategory_obj, _ = VideoSubCategory.objects.get_or_create(
#                     name=subcategory_name, category=category_obj
#                 )

#             view_count = int(stats.get("viewCount", 0))
#             like_count = int(stats.get("likeCount", 0))
#             comment_count = int(stats.get("commentCount", 0))

#             YouTubeVideo.objects.create(
#                 video_id=video_id,
#                 title=title,
#                 description=description,
#                 thumbnail_url=snippet['thumbnails'].get('high', {}).get('url', ''),
#                 published_at=parse_datetime(snippet['publishedAt']),
#                 channel_title=snippet['channelTitle'],
#                 duration=duration,
#                 view_count=view_count,
#                 like_count=like_count,
#                 comment_count=comment_count,
#                 category=category_obj,
#                 subcategory=subcategory_obj
#             )

#             saved += 1
#             titles.append(title)
#             print(f"✅ Saved: {title}")

#         except Exception as e:
#             print(f"❌ Error processing video {video_id}: {e}")
#             continue

#     print(f"✅ Fetched and saved {saved} videos.")
#     return saved, titles


# def get_channel_id_from_video_id(video_id: str) -> str:
#     url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key_youtube}'
#     try:
#         response = requests.get(url)
#         data = response.json()
#         if 'items' in data and len(data['items']) > 0:
#             return data['items'][0]['snippet']['channelId']
#     except Exception as e:
#         print(f"❌ Error getting channel ID for video {video_id}: {e}")

#     return None














# import os
# import isodate
# import requests
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from django.utils.dateparse import parse_datetime
# from decouple import config
# from django.utils.text import slugify

# from api.models import YouTubeVideo, VideoCategory, VideoSubCategory
# from .category_keywords import CATEGORY_KEYWORDS
# from .category_assigner import assign_category
# from .fetch_videos_function import fetch_videos

# # Load API key
# api_key_youtube = config("api_key_youtube")
# YOUTUBE_API_SERVICE_NAME = "youtube"
# YOUTUBE_API_VERSION = "v3"

# def get_youtube_client():
#     return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key_youtube)

# def fetch_videos_by_keywords(youtube, keyword, max_results=10):
#     return youtube.search().list(
#         q=keyword,
#         part="snippet",
#         maxResults=min(max_results, 10),
#         type="video",
#         relevanceLanguage="en",
#         safeSearch="moderate",
#         order="date"
#     ).execute()

# def get_video_details(youtube, video_id):
#     try:
#         video_response = youtube.videos().list(
#             part="snippet,contentDetails,statistics",
#             id=video_id
#         ).execute()
#         return video_response["items"][0] if video_response["items"] else None
#     except Exception as e:
#         print(f"❌ Error fetching details for video {video_id}: {e}")
#         return None


# def fetch_videos_from_channel(channel_id, max_results=50):
#     youtube = get_youtube_client()

#     try:
#         search_response = youtube.search().list(
#             part='snippet',
#             channelId=channel_id,
#             type='video',
#             order='date',
#             maxResults=min(max_results, 50)
#         ).execute()
#     except HttpError as e:
#         print(f"❌ YouTube API Error: {e}")
#         return 0, []
#     except Exception as e:
#         print(f"❌ Unexpected error while fetching videos: {e}")
#         return 0, []

#     saved = 0
#     titles = []

#     for item in search_response.get('items', []):
#         try:
#             video_id = item['id']['videoId']
#             snippet = item['snippet']
#             title = snippet['title']
#             description = snippet.get('description', '')

#             print(f"🔍 Checking video: {video_id} - {title}")

#             details = youtube.videos().list(part='contentDetails,statistics', id=video_id).execute()
#             content_info = details['items'][0]['contentDetails']
#             stats = details['items'][0]['statistics']
#             duration = content_info['duration']

#             if not is_video_long_enough(duration):
#                 print(f"⏭️ Skipping short video: {duration}")
#                 continue

#             if YouTubeVideo.objects.filter(video_id=video_id).exists():
#                 print(f"⚠️ Video already exists: {video_id}")
#                 continue

#             youtube_category_id = ""  # Optional for now
#             category_name, subcategory_name = assign_category(title, description, youtube_category_id)
#             category_obj, _ = VideoCategory.objects.get_or_create(name=category_name)
#             subcategory_obj = None
#             if subcategory_name:
#                 subcategory_obj, _ = VideoSubCategory.objects.get_or_create(name=subcategory_name, category=category_obj)

#             view_count = int(stats.get("viewCount", 0))
#             like_count = int(stats.get("likeCount", 0))
#             comment_count = int(stats.get("commentCount", 0))

#             YouTubeVideo.objects.create(
#                 video_id=video_id,
#                 title=title,
#                 description=description,
#                 thumbnail_url=snippet['thumbnails'].get('high', {}).get('url', ''),
#                 published_at=parse_datetime(snippet['publishedAt']),
#                 channel_title=snippet['channelTitle'],
#                 duration=duration,
#                 view_count=view_count,
#                 like_count=like_count,
#                 comment_count=comment_count,
#                 category=category_obj,
#                 subcategory=subcategory_obj
#             )

#             saved += 1
#             titles.append(title)
#             print(f"✅ Saved: {title}")

#         except Exception as e:
#             print(f"❌ Error processing video {video_id}: {e}")
#             continue

#     print(f"✅ Fetched and saved {saved} videos.")
#     return saved, titles

# def get_channel_id_from_video_id(video_id: str) -> str:
#     url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key_youtube}'
#     try:
#         response = requests.get(url)
#         data = response.json()
#         if 'items' in data and len(data['items']) > 0:
#             return data['items'][0]['snippet']['channelId']
#     except Exception as e:
#         print(f"❌ Error getting channel ID for video {video_id}: {e}")

#     return None
















# import os
# import isodate
# import requests
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from django.utils.dateparse import parse_datetime
# from decouple import config
# from django.utils.text import slugify

# from api.models import YouTubeVideo, VideoCategory, VideoSubCategory
# from .category_keywords import CATEGORY_KEYWORDS
# from .category_assigner import assign_category

# # Load API key
# api_key_youtube = config("api_key_youtube")
# YOUTUBE_API_SERVICE_NAME = "youtube"
# YOUTUBE_API_VERSION = "v3"

# def get_youtube_client():
#     return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key_youtube)

# def fetch_videos_by_keywords(youtube, keyword, max_results=10):
#     return youtube.search().list(
#         q=keyword,
#         part="snippet",
#         maxResults=min(max_results, 10),
#         type="video",
#         relevanceLanguage="en",
#         safeSearch="moderate",
#         order="date"
#     ).execute()

# def get_video_details(youtube, video_id):
#     try:
#         video_response = youtube.videos().list(
#             part="snippet,contentDetails,statistics",
#             id=video_id
#         ).execute()
#         return video_response["items"][0] if video_response["items"] else None
#     except Exception as e:
#         print(f"❌ Error fetching details for video {video_id}: {e}")
#         return None

# def send_to_deepseek(video_data):
#     try:
#         response = requests.post("http://localhost:8080/deepseek-chat", json=video_data)
#         return response.ok
#     except Exception as e:
#         print("❌ Error sending to DeepSeek:", e)
#         return False

# def is_video_long_enough(duration):
#     try:
#         total_seconds = isodate.parse_duration(duration).total_seconds()
#         return total_seconds >= 60
#     except Exception:
#         return False

# def fetch_videos(channel_id=None, max_results=10):
#     youtube = get_youtube_client()
#     total_saved = 0
#     saved_titles = []

#     for category_name, keywords in CATEGORY_KEYWORDS.items():
#         if total_saved >= max_results:
#             break

#         category_obj, _ = VideoCategory.objects.get_or_create(name=category_name)

#         for keyword in keywords:
#             if total_saved >= max_results:
#                 break

#             try:
#                 search_results = fetch_videos_by_keywords(youtube, keyword, max_results=10)

#                 for item in search_results.get("items", []):
#                     if total_saved >= max_results:
#                         break

#                     video_id = item["id"]["videoId"]
#                     snippet = item["snippet"]

#                     if YouTubeVideo.objects.filter(video_id=video_id).exists():
#                         continue

#                     details = get_video_details(youtube, video_id)
#                     if not details:
#                         continue

#                     duration = details["contentDetails"]["duration"]
#                     if not is_video_long_enough(duration):
#                         print(f"⏭️ Skipping short video: {video_id}")
#                         continue

#                     stats = details.get("statistics", {})
#                     view_count = int(stats.get("viewCount", 0))
#                     like_count = int(stats.get("likeCount", 0))
#                     comment_count = int(stats.get("commentCount", 0))

#                     video_data = {
#                         "video_id": video_id,
#                         "title": snippet["title"],
#                         "description": snippet.get("description", ""),
#                         "published_at": snippet["publishedAt"],
#                         "thumbnail_url": snippet["thumbnails"]["high"]["url"],
#                         "channel_title": snippet["channelTitle"],
#                         "duration": duration,  # ISO 8601 string
#                         "view_count": view_count,
#                         "like_count": like_count,
#                         "comment_count": comment_count,
#                         "category": category_obj.name,
#                     }

#                     if send_to_deepseek(video_data):
#                         YouTubeVideo.objects.create(
#                             video_id=video_id,
#                             title=video_data["title"],
#                             description=video_data["description"],
#                             published_at=parse_datetime(video_data["published_at"]),
#                             thumbnail_url=video_data["thumbnail_url"],
#                             channel_title=video_data["channel_title"],
#                             duration=video_data["duration"],
#                             view_count=view_count,
#                             like_count=like_count,
#                             comment_count=comment_count,
#                             category=category_obj,
#                         )
#                         print(f"✅ Saved: {video_data['title']} ({category_name})")
#                         total_saved += 1
#                         saved_titles.append(video_data['title'])
#                     else:
#                         print(f"⚠️ Skipped saving video because DeepSeek failed: {video_data['title']}")

#             except HttpError as e:
#                 print(f"❌ YouTube API error: {e}")
#             except Exception as e:
#                 print(f"❌ Error processing keyword '{keyword}': {e}")

#     return total_saved, saved_titles

# def fetch_videos_from_channel(channel_id, max_results=50):
#     youtube = get_youtube_client()

#     try:
#         search_response = youtube.search().list(
#             part='snippet',
#             channelId=channel_id,
#             type='video',
#             order='date',
#             maxResults=min(max_results, 50)
#         ).execute()
#     except HttpError as e:
#         print(f"❌ YouTube API Error: {e}")
#         return 0, []
#     except Exception as e:
#         print(f"❌ Unexpected error while fetching videos: {e}")
#         return 0, []

#     saved = 0
#     titles = []

#     for item in search_response.get('items', []):
#         try:
#             video_id = item['id']['videoId']
#             snippet = item['snippet']
#             title = snippet['title']
#             description = snippet.get('description', '')

#             print(f"🔍 Checking video: {video_id} - {title}")

#             details = youtube.videos().list(part='contentDetails,statistics', id=video_id).execute()
#             content_info = details['items'][0]['contentDetails']
#             stats = details['items'][0]['statistics']
#             duration = content_info['duration']

#             if not is_video_long_enough(duration):
#                 print(f"⏭️ Skipping short video: {duration}")
#                 continue

#             if YouTubeVideo.objects.filter(video_id=video_id).exists():
#                 print(f"⚠️ Video already exists: {video_id}")
#                 continue

#             youtube_category_id = ""  # Optional for now
#             category_name, subcategory_name = assign_category(title, description, youtube_category_id)
#             category_obj, _ = VideoCategory.objects.get_or_create(name=category_name)
#             subcategory_obj = None
#             if subcategory_name:
#                 subcategory_obj, _ = VideoSubCategory.objects.get_or_create(name=subcategory_name, category=category_obj)

#             view_count = int(stats.get("viewCount", 0))
#             like_count = int(stats.get("likeCount", 0))
#             comment_count = int(stats.get("commentCount", 0))

#             YouTubeVideo.objects.create(
#                 video_id=video_id,
#                 title=title,
#                 description=description,
#                 thumbnail_url=snippet['thumbnails'].get('high', {}).get('url', ''),
#                 published_at=parse_datetime(snippet['publishedAt']),
#                 channel_title=snippet['channelTitle'],
#                 duration=duration,
#                 view_count=view_count,
#                 like_count=like_count,
#                 comment_count=comment_count,
#                 category=category_obj,
#                 subcategory=subcategory_obj
#             )

#             saved += 1
#             titles.append(title)
#             print(f"✅ Saved: {title}")

#         except Exception as e:
#             print(f"❌ Error processing video {video_id}: {e}")
#             continue

#     print(f"✅ Fetched and saved {saved} videos.")
#     return saved, titles

# def get_channel_id_from_video_id(video_id: str) -> str:
#     url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key_youtube}'
#     try:
#         response = requests.get(url)
#         data = response.json()
#         if 'items' in data and len(data['items']) > 0:
#             return data['items'][0]['snippet']['channelId']
#     except Exception as e:
#         print(f"❌ Error getting channel ID for video {video_id}: {e}")

#     return None


# import isodate
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from django.utils.dateparse import parse_datetime
# from decouple import config
# from api.models import YouTubeVideo, VideoCategory, VideoSubCategory  # ✅ Make sure your models are ready

# # ✅ Keywords per custom category
# CATEGORY_KEYWORDS = {
 
# "Quran":[
#   "quran",
#   "holy quran", "day of judgment",
#   "jannah",
#   "jahannam",
#   "signs of the hour",
#   "angels in quran",
#   "jinn in quran",
#   "shaitan in quran",
#   "dua from quran",
#   "quranic supplications",
#   "dhikr","zikr",
#   "barakah from quran","rewards of reading quran",
#   "virtues of quran",
#   "best surah to read",
#   "surah for protection",
#   "surah for healing",
#   "surah for rizq",
#   "surah for anxiety",
#   "surah for forgiveness",
#   "surah for marriage",
#   "night prayer and quran",
#   "tahajjud and quran","tarawih",
#   "quran and youth",
#   "quran and children",
#   "quran and family"
#   "noble quran",
#   "quranic verses",
#   "quran surah",
#   "quran ayah",
#   "tajweed",
#   "tajweed rules",
#   "quran recitation",
#   "quran mp3","quran audio","quran video","quran translation",
#   "quran in english",
#   "quran in arabic",
#   "quran in urdu",
#   "quran in hindi",
#   "quran with tajweed",
#   "quran with translation",
#   "quran with tafsir",
#   "quran explanation",
#   "tafsir",
#   "tafsir ibn kathir",
#   "tafsir al jalalayn",
#   "tafsir as-saadi",
#   "quran learning",
#   "quran education",
#   "learn quran",
#   "teach quran",
#   "quran for kids",
#   "quran for beginners",
#   "quran online",
#   "quran academy",
#   "quran class",
#   "quran memorization",
#   "hifz",
#   "hifz program",
#   "hifz quran","hafiz",
#   "become hafiz",
#   "mushaf",
#   "mushaf madinah",
#   "surah al-fatiha",
#   "surah al-baqarah",
#   "surah yaseen",
#   "surah rahman","surah kahf","surah mulk","surah ikhlas","surah nas","surah falaq","daily quran",
#   "quran verse of the day",
#   "quran quotes",
#   "quran inspiration",
#   "quran motivation",
#   "quran reflection","quran journaling","quran notes","quran study",
#   "quran study group","quran study circle",
#   "quran challenge","quran app","quran website","quranic arabic","classical arabic",
#   "quran dictionary",
#   "quranic grammar","arabic grammar","quranic names","names from quran","prophets in quran",
#   "stories of the prophets",
#   "miracles in quran","science in the quran","quran and science","quran for women",
#   "quran and sunnah",
#   "quran and hadith",
#   "quran and islam","islam","muslim","allah",
#   "prophet muhammad","rasulullah","deen",
#   "iman",
#   "taqwa",
#   "ramadan and quran",
#   "quran and fasting", "quran in prayer", "quran and salah","zakat in quran", "hajj in quran",
 
# ],


# "Technology": [
#   "artificial intelligence", "machine learning", "deep learning", "neural network",
#   "software development", "mobile application", "web app", "smart devices", "robotics","gamers","gamer"
#   "api integration", "frontend development", "backend services",
#   "cybersecurity", "cloud computing", "5g network", "internet of things",
#   "data science", "data analysis",
#   "programming", "coding", "github project", "open source", "full stack",
#   "augmented reality", "virtual reality", "digital innovation", "technology news", "tech gadgets",
#   "elon musk", "mark zuckerberg", "chatgpt", "openai", "tesla", "spacex", "apple iphone", "android development",
#   "python", "javascript", "typescript", "java", "c-language", "c++", "c#", "go", "rust", "php", "ruby", "swift", "kotlin", 
#   "dart", "scala", "r-language", "matlab", "bash", "shell scripting", "perl", "sql", "html", "css", "json", "yaml"
# ],
#     "Education": ["lecture", "study", "education", "learning", "class", "course"],
#     "Business": [
#     "market", "business", "startup", "entrepreneur", "company", "profit",
#     "investment", "venture capital", "stock market", "shareholder", "CEO",
#     "founder", "business model", "monetize", "cash flow", "revenue",
#     "business strategy", "business growth", "financial report", "balance sheet",
#     "sales pitch", "small business", "scaling a business", "digital marketing",
#     "B2B", "B2C", "ecommerce", "merger", "acquisition", "IPO", "business plan",
#     "funding", "pitch deck", "startup idea", "bootstrapping", "angel investor",
#     "business leadership", "profit margin", "supply chain", "branding"
# ],
#     "Politics": [
#     "president", "government", "minister", "election", "prime minister",
#     "politician", "parliament", "senator", "congress", "legislation",
#     "policy making", "voting", "political party", "campaign", "democracy",
#     "dictator", "opposition leader", "diplomacy", "foreign affairs",
#     "international relations", "geopolitics", "political rally", "political debate",
#     "public office", "cabinet reshuffle", "political campaign", "referendum",
#     "human rights", "presidential speech", "government policy", "political corruption",
    
#     # Specific figures & regions
#     "trump", "biden", "putin", "ukraine", "samia suluhu", "mama samia",
#     "tanzania politics", "white house", "state house", "washington dc"
# ],
# "Motivation": [
#   "motivation", "motivational", "inspire", "inspiration", "inspirational",
#   "success", "self-discipline", "self-control", "goal setting", "goal driven",
#   "ambition", "life purpose", "find your why", "achieve your dreams",
#   "overcome challenges", "never give up", "never quit", "grind mode", 
#   "personal growth", "self-growth", "self-improvement", "self-mastery",
#   "mindset shift", "positive mindset", "growth mindset", "winning mindset",
#   "stay focused", "laser focus", "clarity of purpose", "take action",
#   "productivity", "work ethic", "inner drive", "willpower", "self-belief",
#   "confidence", "believe in yourself", "push yourself", "level up",
#   "rise above", "be your best", "dream big", "vision board", 
#   "unlock your potential", "live with purpose", "discipline", "consistency",
#   "daily habits", "habits of success", "routine", "morning routine",
#   "unstoppable", "determination", "grit", "resilience", "mental toughness",
#   "perseverance", "mental clarity", "mental strength", "attitude shift",
#   "attitude of gratitude", "self-confidence", "empower yourself", "empowerment",
#   "transform your life", "change your life", "new beginnings", "breakthrough",
#   "take control", "life transformation", "motivational speech", "inspiring stories",
#   "motivational speaker", "success story", "rise and grind", "chase your dreams",
#   "keep going", "fuel your fire", "inner power", "mind power", "focus on success",
#   "no excuses", "get it done", "discipline equals freedom", "be legendary",
#   "neuroscientist", "mindset training", "mental discipline", "growth through struggle",
#   "bounce back", "long-term thinking", "inner focus", "personal excellence",
#   "relentless", "no pain no gain", "find your strength", "strength within",
#   "motivate your mind", "feel better", "power through", "ignite your passion",
#   "strong mindset", "stay hungry", "never settle", "be unstoppable","Motivational","Don't Waste Your Youth",
# ],

#     "Languages": [
#     # General Language Learning
#   "language learning", "learn languages", "language skills", "foreign language",
#   "language tips", "language hacks", "vocabulary building", "language fluency",
#   "language practice", "pronunciation", "language mastery", "language acquisition",
#   "language habits", "language goals", "daily language practice", "language immersion",
#   "grammar tips", "language tutor", "language coach", "polyglot", "multilingual",
#   "self-study language", "language exposure", "language routine", "language challenge",
#   "conversational fluency", "memorize vocabulary", "language boost", "love languages",
#   "language motivation", "language learners", "learn fast", "language journey",

#   # English Specific
#   "learn english","english","vocabulary","british english","slang words in British english","how to talk like","slang",
#   "english culture","sentence","french words","languages","language", "english grammar", "pronounce"
#   "improve your english", "english speaking","england","great britain","sounding ","sounds","sound",
#   "speak english fluently", "english conversation", "daily english", "basic english",
#   "english pronunciation", "english vocabulary",

#   # French
#   "learn french", "french language", "french grammar", "speak french", "french basics",
#   "daily french", "french conversation",

#   # Spanish
#   "learn spanish", "spanish language", "spanish grammar", "speak spanish", "spanish basics",
#   "daily spanish", "spanish conversation",

#   # Swahili
#   "learn swahili", "kiswahili", "swahili grammar", "speak swahili", "daily swahili",

#   # Arabic
#    "learn arabic", "arabic language", "arabic for beginners", "arabic grammar",
#   "arabic speaking", "arabic conversation", "arabic pronunciation", "modern standard arabic",
#   "arabic vocabulary", "arabic words", "arabic phrases", "arabic verbs", "arabic alphabet",
#   "arabic script", "arabic calligraphy", "speak arabic", "arabic fluency",
#   "how to speak arabic", "arabic language tips", "daily arabic", "arabic lessons",
#   "arabic course", "arabic tutorial", "arabic teacher", "arabic practice",
#   "arabic study", "arabic dialogue", "arabic sentence structure",
#   "quranic arabic", "fus'ha arabic", "classical arabic", "arabic reading",
#   "arabic writing", "arabic comprehension", "arabic listening", "arabic speaking skills",
#   "arabic learning app", "arabic flashcards", "memorize arabic", "arabic challenge",
#   "arabic translation", "arabic to english", "english to arabic",

# # Native Arabic Keywords (Modern Standard & Quranic
#   "تعلم العربية", "تعلم اللغة العربية", "تكلم العربية", "اللغة العربية",
#   "قواعد اللغة العربية", "النحو", "الصرف", "كلمات عربية", "مفردات عربية",
#   "عبارات عربية", "أفعال عربية", "الحروف الأبجدية", "الكتابة بالعربية",
#   "القراءة بالعربية", "الاستماع بالعربية", "التحدث بالعربية", "فصحى",
#   "العربية الفصحى", "العربية الكلاسيكية", "العربية القرآنية", "آيات قرآنية",
#   "معاني الكلمات", "شرح كلمات", "ترجمة عربية", "تمارين عربية", "دروس عربية",
#   "معلم اللغة العربية", "تعليم اللغة العربية", "أحاديث بالعربية", "محادثة عربية",
#   "جمل عربية", "دورة لغة عربية", "فهم العربية", "مفردات قرآنية", "تفسير اللغة العربية",
#   "إملاء عربي", "اللغة العربية للمبتدئين", "كورس لغة عربية", "تعليم القراءة بالعربية",
#   "كلمات من القرآن", "فهم القرآن", "النحو العربي", "العربية للأطفال", "تعليم القرآن بالعربية"

# # Chinese
#   "learn chinese", "mandarin chinese", "chinese grammar", "speak chinese", "chinese pronunciation",
#   "chinese tones", "chinese vocabulary", "chinese characters", "daily chinese",
#   "chinese conversation", "simplified chinese", "traditional chinese", "学中文", "汉语", "说中文",
#   "学习汉语", "中文词汇", "中文发音",
# ],


# "Health": [
#     "health", "healthy lifestyle", "fitness", "workout", "diet", "exercise",
#     "mental health", "wellness", "nutrition", "self-care", "mindfulness",
#     "stress relief", "meditation", "anxiety", "depression", "emotional health",
#     "yoga", "bodybuilding", "weight loss", "healthy habits", "immune system"
# ],

# "Sports": [
#     "sports", "football", "soccer", "nba", "basketball", "cricket", "match",
#     "goal", "athletes", "team", "tournament", "competition", "league",
#     "world cup", "fifa", "olympics", "championship", "game highlights", "score"
# ],

# "Music": [
#     "music", "song", "album", "musician", "singer", "track", "melody", "lyrics",
#     "composer", "band", "concert", "instrumental", "live performance", "dj",
#     "playlist", "beats", "rap", "hip hop", "pop song", "music video"
# ],

# "War": [
#     "war", "conflict", "battle", "military", "combat", "soldiers", "army",
#     "navy", "air force", "violence", "fighting", "peace", "gaza", "israel",
#     "ukraine", "russia", "invasion", "weapons", "bomb", "troops", "clashes"
# ],

# "Poverty": [
#     "poverty", "hunger", "homeless", "unemployed", "slums", "underprivileged",
#     "disadvantaged", "social justice", "economic inequality", "charity",
#     "donation", "nonprofit", "support the poor", "basic needs", "humanitarian",
#     "famine", "low income", "struggle", "help the needy"
# ],

# "Children": [
#     "children", "kids", "youth", "childcare", "parenting", "education for children",
#     "child development", "nursery", "family", "baby", "youth empowerment",
#     "childhood", "toddlers", "school kids", "child rights", "students"
# ],

    


# }

# YOUTUBE_CATEGORY_MAP = {
#     "1": "Film & Animation",
#     "2": "Autos & Vehicles",
#     "10": "Music",
#     "15": "Pets & Animals",
#     "17": "Sports",
#     "18": "Short Movies",
#     "19": "Travel & Events",
#     "20": "Gaming",
#     "21": "Videoblogging",
#     "22": "People & Blogs",
#     "23": "Comedy",
#     "24": "Entertainment",
#     "25": "News & Politics",
#     "26": "How-to & Style",
#     "27": "Education",
#     "28": "Science & Technology",
#     "29": "Nonprofits & Activism",
#     "30": "Movies",
#     "31": "Animes",
#     "32": "Action & Adventure",
#     "33": "Classics",
#     "34": "Documentary",
#     "35": "Drama",
#     "36": "Family",
#     "37": "Foreign",
#     "38": "Horror",
#     "39": "Independent",
#     "40": "Romance",
#     "41": "Sci-Fi & Fantasy",
#     "42": "Thriller",
#     "43": "Mystery",
#     "44": "Game Show",
#     "45": "Reality",
#     "46": "Soap Opera",
#     "47": "Talk Show",
#     "48": "Lifestyle",
#     "49": "Vlog",
#     "50": "Music Video",
#     "51": "Live Music",
#     "52": "Experimental",
#     "53": "Electronic"
# }

# def is_video_long_enough(duration_str):
#     """Minimum video length check (70 seconds for demo, can be changed to 300 for 5 min)."""
#     try:
#         duration = isodate.parse_duration(duration_str)
#         return duration.total_seconds() >= 70
#     except Exception as e:
#         print(f"Duration parse error: {e}")
#         return False

# def assign_category(title, description, youtube_category_id):
#     """Assign category & subcategory from keywords or fallback to YouTube category ID."""
#     text = f"{title} {description}".lower()

#     for category_name, keywords in CATEGORY_KEYWORDS.items():
#         for keyword in keywords:
#             if keyword in text:
#                 return category_name, keyword.capitalize()

#     fallback = YOUTUBE_CATEGORY_MAP.get(youtube_category_id, "Uncategorized")
#     return fallback, None

# def fetch_videos(channel_id, max_results=10):
#     """Main function to fetch and save videos from a channel."""
#     api_key = config("api_key_youtube")
#     if not api_key:
#         raise ValueError("Missing YouTube API Key in .env")

#     youtube = build('youtube', 'v3', developerKey=api_key)

#     try:
#         search_response = youtube.search().list(
#             part='snippet',
#             channelId=channel_id,
#             type='video',
#             order='date',
#             maxResults=max_results
#         ).execute()
#     except HttpError as e:
#         print(f"YouTube API Error: {e}")
#         return 0, []

#     saved = 0
#     titles = []

#     for item in search_response.get('items', []):
#         video_id = item['id']['videoId']
#         snippet = item['snippet']
#         title = snippet['title']
#         description = snippet.get('description', '')
#         youtube_category_id = snippet.get('categoryId', '')

#         print(f"Checking video: {video_id} - {title}")

#         try:
#             video_data = youtube.videos().list(part='contentDetails', id=video_id).execute()
#             content_info = video_data.get('items', [])[0]['contentDetails']
#             duration = content_info.get('duration')

#             if not is_video_long_enough(duration):
#                 print(f"Skipping short video: {duration}")
#                 continue
#         except Exception as e:
#             print(f"Failed fetching duration for {video_id}: {e}")
#             continue

#         if YouTubeVideo.objects.filter(video_id=video_id).exists():
#             print(f"Video already exists: {video_id}")
#             continue

#         # Category & Subcategory assignment
#         category_name, subcategory_name = assign_category(title, description, youtube_category_id)
#         category_obj, _ = VideoCategory.objects.get_or_create(name=category_name)
#         subcategory_obj = None
#         if subcategory_name:
#             subcategory_obj, _ = VideoSubCategory.objects.get_or_create(name=subcategory_name, category=category_obj)

#         # Save to DB
#         video = YouTubeVideo.objects.create(
#             video_id=video_id,
#             title=title,
#             description=description,
#             thumbnail_url=snippet['thumbnails'].get('high', {}).get('url', ''),
#             published_at=parse_datetime(snippet['publishedAt']),
#             channel_title=snippet['channelTitle'],
#             category=category_obj,
#             subcategory=subcategory_obj
#         )

#         saved += 1
#         titles.append(title)
#         print(f"Saved: {title}")

#     print(f"✅ Fetched and saved {saved} videos.")
#     return saved, titles




# # your_app/utility/fetch_youtube_videos.py
# import requests
# from decouple import config
# def get_channel_id_from_video_id(video_id: str) -> str:
#     """
#     Uses YouTube Data API to get the channel ID from a video ID.
#     """
#     api_key = config("api_key_youtube")  # Replace with your actual API key
#     url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}'

#     response = requests.get(url)
#     data = response.json()

#     if 'items' in data and len(data['items']) > 0:
#         return data['items'][0]['snippet']['channelId']
#     return None


