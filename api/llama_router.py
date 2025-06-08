from openai import OpenAI
from decouple import config
from api.models import YouTubeVideo
from api.focus_message import system_message  # Customize this if needed

# Initialize LLaMA via OpenRouter
client = OpenAI(
    api_key=config("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://focustube.online",
        "X-Title": "FocusTube"
    }
)

def recommend_best_video(user_query):
    try:
        # Step 1: Ask LLaMA to classify niche
        niche_prompt = (
            f"You are a smart classifier.\n"
            f"A user asked: \"{user_query}\"\n\n"
            f"From the following categories, choose the best match:\n"
            f"Motivation, Technology, Quran, Education, Politics, Business, Programming, Languages, Kids\n\n"
            f"Just return one word: the category name."
        )

        niche_response = client.chat.completions.create(
            model="meta-llama/llama-3-70b-instruct",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": niche_prompt},
            ]
        )
        predicted_niche = niche_response.choices[0].message.content.strip()

        # Step 2: Get videos from that niche
        matching_videos = YouTubeVideo.objects.filter(
            category__name__iexact=predicted_niche,
            status="approved"
        ).order_by("-published_at")[:6]

        video_list = [
            {
                "title": v.title,
                "video_id": v.video_id,
                "thumbnail_url": v.thumbnail_url,
                "summary": v.description[:150] + "..." if v.description else "",
                "watch_url": f"https://www.youtube.com/watch?v={v.video_id}",
                "affiliate_url": f"https://focustube.online/deals/{v.video_id}"
            }
            for v in matching_videos
        ]

        # Step 3: Ask LLaMA for topic + affiliate suggestions
        recommendation_prompt = (
            f"The user is interested in: \"{user_query}\", which maps to the '{predicted_niche}' niche.\n\n"
            f"Recommend:\n"
            f"1. Related video topics\n"
            f"2. Affiliate product ideas\n\n"
            f"Be concise and helpful."
        )

        final_response = client.chat.completions.create(
            model="meta-llama/llama-3-70b-instruct",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": recommendation_prompt},
            ]
        )

        return {
            "niche": predicted_niche,
            "videos": video_list,
            "llama_response": final_response.choices[0].message.content.strip()
        }

    except Exception as e:
        return {"error": f"❌ Error using LLaMA or DB: {str(e)}"}


# import os
# import sys
# import django

# # ✅ Setup Django environment
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "focustubeBase.settings")
# django.setup()

# from openai import OpenAI
# from decouple import config
# from api.models import YouTubeVideo
# from api.focus_message import system_message  # A guiding system prompt for GPT

# # ✅ Setup OpenRouter with GPT
# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=config("OPENROUTER_API_KEY"),
#     default_headers={
#         "HTTP-Referer": "https://focustube.online",
#         "X-Title": "FocusTube"
#     }
# )

# # 🔍 Classify user query first
# def classify_user_query(user_query):
#     try:
#         classification_prompt = f"""
# Classify the user query as either:

# - "video" → if the user is asking for learning, advice, help, topic ideas, or motivation
# - "info" → if the user is asking about FocusTube, saying hello, asking who you are, or greeting

# Just return one word: video or info.

# Query: "{user_query}"
# """
#         response = client.chat.completions.create(
#             model="openai/gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant that classifies queries."},
#                 {"role": "user", "content": classification_prompt}
#             ],
#             max_tokens=10,
#             temperature=0.0
#         )

#         classification = response.choices[0].message.content.strip().lower()
#         return classification
#     except Exception as e:
#         print("❌ Classification error:", str(e))
#         return "video"  # Default to video to be safe

# # 🔍 Main recommendation logic
# def recommend_best_video(user_query):
#     print("🔍 User Query:", user_query)

#     # ✅ Step 0: First classify intent
#     intent = classify_user_query(user_query)
#     print("🧠 Detected Intent:", intent)

#     if intent == "info":
#         return {
#             "response": "I am FocusTube, your intelligent assistant, proudly created by Maulidi Mdami.",
#             "videos": []
#         }

#     # ✅ Step 1: Get top 20 latest approved videos with descriptions
#     videos = YouTubeVideo.objects.filter(status="approved").exclude(description="").order_by("-published_at")[:20]
#     if not videos.exists():
#         return {"error": "❌ No approved videos found in the database."}

#     # ✅ Step 2: Prepare context for LLM
#     video_context = ""
#     for video in videos:
#         video_context += (
#             f"Title: {video.title}\n"
#             f"Description: {video.description}\n"
#             f"ID: {video.video_id}\n\n"
#         )

#     # ✅ Step 3: Create prompt
   

#     # ✅ Step 4: Send to GPT-3.5 via OpenRouter
#     try:
#         response = client.chat.completions.create(
#             model="openai/gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=100,
#             temperature=0.7,
#         )

#         reply = response.choices[0].message.content.strip()
#         print("🤖 GPT-3.5 Response:\n", reply)

#         if not reply:
#             return {"error": "⚠️ GPT-3.5 returned an empty response."}
#         elif "https://www.youtube.com/watch" not in reply:
#             print("⚠️ Full Response:\n", reply)
#             return {"error": "⚠️ GPT-3.5 returned response but no YouTube links found."}

#         return reply

#     except Exception as e:
#         print("❌ GPT Error:", str(e))
#         return {"error": str(e)}

# # 🧪 Run from CLI
# if __name__ == "__main__":
#     query = input("Enter your query: ")
#     result = recommend_best_video(query)
#     print("\n📦 Final Output:\n", result)
