# import os
# import django
# from decouple import config
# from openai import OpenAI

# # ✅ Set Django settings before importing models
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "focustubeBase.settings")
# django.setup()

# from api.models import YouTubeVideo

# # ✅ System prompt: strict instruction for LLaMA
# system_message = (
#     "You are FocusTube's classification engine. You must always respond with exactly one valid category "
#     "from the provided list and never return any other text. Be strict and minimal."
# )

# # ✅ Valid categories to classify into
# VALID_CATEGORIES = [
#     "Motivation", "Technology", "Quran", "Education",
#     "Politics", "Business", "Programming", "Languages", "Kids"
# ]

# # ✅ Initialize LLaMA/OpenRouter client
# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=config("OPENROUTER_API_KEY"),
#     default_headers={
#         "HTTP-Referer": "https://focustube.online",  # Your domain
#         "X-Title": "FocusTube"
#     }
# )

# # ✅ Utility function to validate category result
# def clean_category(cat):
#     return cat.strip().title() if cat.strip().title() in VALID_CATEGORIES else None

# # ✅ Main handler function
# def get_topic_recommendations(user_query):
#     # Step 1: Ask LLaMA to classify the user query
#     niche_prompt = (
#         f"Only return one category name from this list exactly: {', '.join(VALID_CATEGORIES)}.\n"
#         f"User input: {user_query}\n\n"
#         f"Respond with ONE WORD ONLY from the list. No explanations. No formatting."
#     )

#     try:
#         niche_response = client.chat.completions.create(
#             model="meta-llama/llama-2-70b-chat",
#             messages=[
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": niche_prompt},
#             ],
#             stream=False,
#             max_tokens=20
#         )

#         raw_response = niche_response.choices[0].message.content.strip()
#         print("📌 Raw category response:", raw_response)

#         predicted_niche = clean_category(raw_response)

#         if not predicted_niche:
#             return {"error": f"⚠️ Invalid category from LLaMA: '{raw_response}'"}

#         # Step 2: Fetch matching videos from DB
#         matching_videos = YouTubeVideo.objects.filter(
#             category__name__iexact=predicted_niche,
#             status="approved"
#         )[:6]

#         video_list = [
#             {
#                 "title": v.title,
#                 "video_id": v.video_id,
#                 "thumbnail_url": v.thumbnail_url,
#             }
#             for v in matching_videos
#         ]

#         # Step 3: Ask LLaMA for related topics and affiliate suggestions
#         general_prompt = (
#             f"The user is interested in: '{user_query}', which maps to the '{predicted_niche}' niche.\n\n"
#             f"Please provide:\n"
#             f"1. Related video topics (bullet list)\n"
#             f"2. Affiliate product ideas (bullet list)"
#         )

#         final_response = client.chat.completions.create(
#             model="meta-llama/llama-2-70b-chat",
#             messages=[
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": general_prompt},
#             ],
#             stream=False,
#             max_tokens=300
#         )

#         return {
#             "niche": predicted_niche,
#             "videos": video_list,
#             "llama_response": final_response.choices[0].message.content.strip()
#         }

#     except Exception as e:
#         print("❌ LLaMA Recommendation Error:", str(e))
#         return {"error": f"❌ Error from LLaMA or DB: {str(e)}"}

# # ✅ Manual test
# if __name__ == "__main__":
#     query = input("🔍 Enter a topic: ")
#     result = get_topic_recommendations(query)
#     print("\n🎯 LLaMA Recommendation Result:")
#     print(result)

# # recommendation_service.py

# import os
# import django

# # ✅ This must be at the very top
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "focustubeBase.settings")
# django.setup()

# from openai import OpenAI
# from decouple import config
# from api.models import YouTubeVideo
# from api.focus_message import system_message  # Customize this as needed

# # Initialize DeepSeek API
# client = OpenAI(
#     api_key=config("OPENROUTER_API_KEY"),
#     base_url="https://api.deepseek.com"
# )
# def get_topic_recommendations(user_query):
#     # Step 1: Ask DeepSeek to identify niche
#     niche_prompt = (
#         f"A user asked: '{user_query}'.\n"
#         f"From the following categories, which one best matches this query?\n"
#         f"Categories: Motivation, Technology, Quran, Education, Politics, Business, Programming, Languages, Kids\n\n"
#         f"Just reply with the single best category name."
#     )

#     try:
#         niche_response = client.chat.completions.create(
#             model="deepseek-reasoner",
#             messages=[
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": niche_prompt},
#             ],
#             stream=False
#         )
#         predicted_niche = niche_response.choices[0].message.content.strip()

#         # Step 2: Get videos from that niche
#         matching_videos = YouTubeVideo.objects.filter(
#             category__name__iexact=predicted_niche,  # or adapt to your field name
#             status="approved"
#         )[:6]

#         video_list = [
#             {
#                 "title": v.title,
#                 "video_id": v.video_id,
#                 "thumbnail_url": v.thumbnail_url,
#             }
#             for v in matching_videos
#         ]

#         # Step 3: Ask DeepSeek for recommendations too
#         general_prompt = (
#             f"A user is interested in: '{user_query}' which maps to the '{predicted_niche}' niche.\n"
#             f"Please recommend:\n"
#             f"1. Related video topics.\n"
#             f"2. Affiliate product ideas.\n"
#         )

#         final_response = client.chat.completions.create(
#             model="deepseek-chat",
#             messages=[
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": general_prompt},
#             ],
#             stream=False
#         )

#         return {
#             "niche": predicted_niche,
#             "videos": video_list,
#             "deepseek_response": final_response.choices[0].message.content
#         }

#     except Exception as e:
#         return {"error": f"❌ Error from DeepSeek or DB: {e}"}



