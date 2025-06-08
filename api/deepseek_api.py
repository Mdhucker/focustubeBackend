

# import os
# import requests
# from dotenv import load_dotenv
# from openai import OpenAI
# from decouple import config
# from .focus_message import system_message
# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry

# # Load environment variables
# load_dotenv()

# # ----------------------------
# # Setup OpenAI Client for DeepSeek
# # ----------------------------
# client = OpenAI(
#     api_key=config("LLAMMA_API_KEY"),
#     base_url="https://api.deepseek.com"
# )

# # ----------------------------
# # Function 1: General Question
# # ----------------------------
# def ask_deepseek(prompt):
#     LLAMMA_API_KEY = os.getenv("LLAMMA_API_KEY")
#     if not LLAMMA_API_KEY:
#         return "Error: DeepSeek API key is missing."

#     url = "https://api.deepseek.com/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {LLAMMA_API_KEY}",
#         "Content-Type": "application/json",
#     }

#     data = {
#         "model": "deepseek-chat",  # Use faster model for general Q&A
#         "messages": [
#             {
#                 "role": "system",
#                 "content": (
#                     "You are FocusTube, a smart educational assistant built into the FocusTube platform. "
#                     "You help users understand, explore, and learn from motivational and educational YouTube videos. "
#                     "If asked who you are, always respond: 'I am FocusTube, your intelligent assistant.'"
#                 )
#             },
#             {"role": "user", "content": prompt}
#         ],
#         "max_tokens": 300
#     }

#     # Retry logic with timeout
#     session = requests.Session()
#     retries = Retry(
#         total=3,
#         backoff_factor=0.5,
#         status_forcelist=[429, 500, 502, 503, 504],
#         allowed_methods=["POST"]
#     )
#     session.mount("https://", HTTPAdapter(max_retries=retries))

#     try:
#         response = session.post(url, headers=headers, json=data, timeout=10)
#         if response.status_code != 200:
#             return f"API Error {response.status_code}: {response.text}"

#         result = response.json()
#         return result['choices'][0]['message']['content']

#     except Exception as e:
#         return f"Error calling DeepSeek: {str(e)}"


# # ----------------------------
# # Function 2: Categorization
# # ----------------------------
# def send_to_deepseek(video_data):
#     try:
#         title = video_data.get("title", "")
#         description = video_data.get("description", "")
#         short_desc = description[:200]  # Trim for speed

#         prompt = (
#             f"What is the most relevant category or tag for this YouTube video?\n"
#             f"Title: {title}\n"
#             f"Description: {short_desc}"
#         )

#         response = client.chat.completions.create(
#             model="deepseek-chat",
#             messages=[
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": prompt},
#             ],
#             max_tokens=100,
#             stream=False
#         )

#         reply = response.choices[0].message.content
#         print("🤖 DeepSeek response:", reply)
#         return reply  # return content instead of just True for usage

#     except Exception as e:
#         print("❌ Error sending to DeepSeek:", e)
#         return None


# # ----------------------------
# # Example Usage
# # ----------------------------
# if __name__ == "__main__":
#     prompt = "Who are you?"
#     response = ask_deepseek(prompt)
#     print("DeepSeek response:")
#     print(response)

#     video_sample = {
#         "title": "Master Your Mindset in 2024 | Top Motivational Talk",
#         "description": "This video explores how your thoughts shape your reality and how to rewire your thinking for success and growth."
#     }
#     category = send_to_deepseek(video_sample)
#     print("Suggested Category:")
#     print(category)

