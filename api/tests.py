# import sys
# import os
# import django
# import numpy as np
# from openai import OpenAI
# from decouple import config

# # Setup Django environment
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'focustubeBase.settings')
# django.setup()

# from api.models import YouTubeVideo
# from api.focus_message import system_message  # Customize your system prompt here
# from api.faiss_index import build_faiss_index

# # ✅ OpenRouter-compatible client
# client = OpenAI(
#     api_key=config("OPENROUTER_API_KEY"),
#     base_url="https://openrouter.ai/api/v1",
#     default_headers={
#         "HTTP-Referer": "https://focustube.online",
#         "X-Title": "FocusTube"
#     }
# )

# # ✅ Embedding function using OpenRouter-supported model

# def get_embedding(text):
#     response = client.embeddings.create(
#         model="openai/text-embedding-3-small",  # OpenRouter supports this via proxy
#         input=text
#     )
#     return np.array(response.data[0].embedding, dtype=np.float32)

# # ✅ FAISS-based local video search
# def search_similar_videos(user_query, top_k=5):
#     query_embedding = get_embedding(user_query)
#     index, video_ids = build_faiss_index()

#     if index is None:
#         print("No FAISS index built.")
#         return []

#     D, I = index.search(np.array([query_embedding]), top_k)
#     matched_ids = [video_ids[i] for i in I[0] if i != -1]
#     return YouTubeVideo.objects.filter(id__in=matched_ids)

# # ✅ LLaMA-powered full recommendation flow
# def recommend_best_video(user_query):
#     try:
#         # Step 1: Classify niche
#         niche_prompt = (
#             f"You are a smart classifier.\n"
#             f"A user asked: \"{user_query}\"\n\n"
#             f"From the following categories, choose the best match:\n"
#             f"Motivation, Technology, Quran, Education, Politics, Business, Programming, Languages, Kids\n\n"
#             f"Just return one word: the category name."
#         )

#         niche_response = client.chat.completions.create(
#             model="meta-llama/llama-3-70b-instruct",
#             messages=[
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": niche_prompt},
#             ]
#         )
#         predicted_niche = niche_response.choices[0].message.content.strip()

#         # Step 2: Get matching videos from DB
#         matching_videos = YouTubeVideo.objects.filter(
#             category__name__iexact=predicted_niche,
#             status="approved"
#         ).order_by("-published_at")[:6]

#         video_list = [
#             {
#                 "title": v.title,
#                 "video_id": v.video_id,
#                 "thumbnail_url": v.thumbnail_url,
#                 "summary": v.description[:150] + "..." if v.description else "",
#                 "watch_url": f"https://www.youtube.com/watch?v={v.video_id}",
#                 "affiliate_url": f"https://focustube.online/deals/{v.video_id}"
#             }
#             for v in matching_videos
#         ]

#         # Step 3: Ask LLaMA for related topics + affiliate ideas
#         final_prompt = (
#             f"The user is interested in: \"{user_query}\" (niche: {predicted_niche}).\n\n"
#             f"Please suggest:\n"
#             f"1. Related video topics\n"
#             f"2. Affiliate product ideas\n"
#             f"Be concise and helpful."
#         )

#         final_response = client.chat.completions.create(
#             model="meta-llama/llama-3-70b-instruct",
#             messages=[
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": final_prompt},
#             ]
#         )

#         return {
#             "niche": predicted_niche,
#             "videos": video_list,
#             "llama_response": final_response.choices[0].message.content.strip()
#         }

#     except Exception as e:
#         return {"error": f"❌ LLaMA or DB error: {str(e)}"}

# # ✅ Optional CLI test
# if __name__ == "__main__":
#     query = "how to improve focus and productivity"
#     print(f"User Query: {query}")

#     print("\n🔍 Similar Videos (FAISS):")
#     videos = search_similar_videos(query)
#     for v in videos:
#         print(f"- {v.title} → https://youtube.com/watch?v={v.video_id}")

#     print("\n🦙 LLaMA Recommendation:")
#     result = recommend_best_video(query)
#     if "error" in result:
#         print(result["error"])
#     else:
#         print("Predicted Niche:", result["niche"])
#         print("\nTop Videos:")
#         for v in result["videos"]:
#             print(f"- {v['title']} → {v['watch_url']}")
#         print("\nSuggestions from LLaMA:")
#         print(result["llama_response"])
