# import isodate
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from decouple import config
# from django.utils.text import slugify
# from api.models import YouTubeVideo, VideoCategory, VideoSubCategory

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


# def detect_category(text):
#     text_lower = text.lower()
#     for category, keywords in CATEGORY_KEYWORDS.items():
#         for keyword in keywords:
#             if keyword.lower() in text_lower:
#                 return category, None  # Add subcategory logic later
#     return "Uncategorized", None


# def fetch_single_video(video_id):
#     api_key = config("YOUTUBE_API_KEY")

#     try:
#         youtube = build("youtube", "v3", developerKey=api_key)
#         request = youtube.videos().list(
#             part="snippet,contentDetails,statistics",
#             id=video_id,
#         )
#         response = request.execute()
#         items = response.get("items")

#         if not items:
#             return False, f"No video found with ID: {video_id}"

#         data = items[0]
#         snippet = data["snippet"]
#         stats = data.get("statistics", {})
#         duration = isodate.parse_duration(data["contentDetails"]["duration"]).total_seconds()

#         title = snippet["title"]
#         description = snippet["description"]
#         tags = snippet.get("tags", [])
#         category_name, subcategory_name = detect_category(title + " " + description + " " + " ".join(tags))

#         category_obj, _ = VideoCategory.objects.get_or_create(
#             name=category_name, defaults={"slug": slugify(category_name)}
#         )

#         subcategory_obj = None
#         if subcategory_name:
#             subcategory_obj, _ = VideoSubCategory.objects.get_or_create(
#                 name=subcategory_name, category=category_obj, defaults={"slug": slugify(subcategory_name)}
#             )

#         video, created = YouTubeVideo.objects.update_or_create(
#             video_id=video_id,
#             defaults={
#                 "title": title,
#                 "description": description,
#                 "duration": duration,
#                 "published_at": snippet["publishedAt"],
#                 "view_count": stats.get("viewCount", 0),
#                 "like_count": stats.get("likeCount", 0),
#                 "thumbnail": snippet["thumbnails"]["high"]["url"],
#                 "channel_title": snippet["channelTitle"],
#                 "status": "pending",
#                 "category": category_obj,
#                 "subcategory": subcategory_obj,
#             },
#         )

#         return True, f"Video '{title}' {'created' if created else 'updated'} successfully"

#     except HttpError as e:
#         return False, f"API Error: {e}"
#     except Exception as e:
#         return False, f"Unexpected error: {e}"
