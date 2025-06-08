
# from .subcategory_matcher import match_subcategory  # Make sure this import is correct

def fetch_videos(channel_id=None, max_results=10):
    youtube = get_youtube_client()
    total_saved = 0
    saved_titles = []

    for category_name, keywords in CATEGORY_KEYWORDS.items():
        if total_saved >= max_results:
            break

        for keyword in keywords:
            if total_saved >= max_results:
                break

            try:
                search_results = fetch_videos_by_keywords(youtube, keyword, max_results=10)

                for item in search_results.get("items", []):
                    if total_saved >= max_results:
                        break

                    video_id = item["id"]["videoId"]
                    snippet = item["snippet"]

                    if YouTubeVideo.objects.filter(video_id=video_id).exists():
                        continue

                    details = get_video_details(youtube, video_id)
                    if not details:
                        continue

                    duration = details["contentDetails"]["duration"]
                    if not is_video_long_enough(duration):
                        print(f"⏭️ Skipping short video: {video_id}")
                        continue

                    stats = details.get("statistics", {})
                    view_count = int(stats.get("viewCount", 0))
                    like_count = int(stats.get("likeCount", 0))
                    comment_count = int(stats.get("commentCount", 0))

                    # Match subcategory using semantic logic
                    main_category, subcategory = match_subcategory(
                        snippet["title"], snippet.get("description", "")
                    )

                    # Get or create VideoCategory and Subcategory
                    main_cat_obj, _ = VideoCategory.objects.get_or_create(name=main_category)
                    sub_cat_obj, _ = VideoSubCategory.objects.get_or_create(
                        name=subcategory, main_category=main_cat_obj
                    )

                    YouTubeVideo.objects.create(
                        video_id=video_id,
                        title=snippet["title"],
                        description=snippet.get("description", ""),
                        published_at=parse_datetime(snippet["publishedAt"]),
                        thumbnail_url=snippet["thumbnails"]["high"]["url"],
                        channel_title=snippet["channelTitle"],
                        duration=duration,
                        view_count=view_count,
                        like_count=like_count,
                        comment_count=comment_count,
                        category=main_cat_obj,
                        subcategory=sub_cat_obj,
                    )
                    print(f"✅ Saved: {snippet['title']} ({main_category} → {subcategory})")
                    total_saved += 1
                    saved_titles.append(snippet['title'])

            except HttpError as e:
                print(f"❌ YouTube API error: {e}")
            except Exception as e:
                print(f"❌ Error processing keyword '{keyword}': {e}")

    return total_saved, saved_titles


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
