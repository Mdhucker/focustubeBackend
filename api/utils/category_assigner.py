
# def assign_category(title, description, youtube_category_id):
#     """
#     Assigns a category and subcategory based on title/description/YouTube category ID.
#     """
#     text = f"{title} {description}".lower()

#     # Quran
#     if "politics" in text or "politics world" in text:
#         return "Politics", "politicians"

#     # Motivation
#     elif "motivation" in text or "self improvement" in text:
#         return "Motivation", "Self Improvement"

#     # Languages
#     elif any(keyword in text for keyword in [
#         "language learning", "learn languages", "english grammar", "spoken english",
#         "learn english", "basic english", "english conversation", "english speaking practice",
#         "swahili lessons", "learn swahili", "french lessons", "learn french", "german language",
#         "learn german", "spanish course", "learn spanish", "arabic language", "learn arabic",
#         "chinese for beginners", "learn chinese", "mandarin lessons", "italian language",
#         "learn italian", "hindi language", "learn hindi", "russian lessons", "learn russian",
#         "korean language", "learn korean", "japanese for beginners", "learn japanese",
#         "language tips", "language tricks", "english vocabulary", "pronunciation practice",
#         "language hacks", "duolingo", "polyglot tips", "language apps", "foreign language learning",
#         "language exchange", "multilingual learning", "language immersion"
#     ]):
#         return "Languages", "Language Learning"

#     elif any(keyword in text.lower() for keyword in [
#         "quran", "qur'an", "holy quran", "al-quran", "alquran", "the quran",
#         "recitation", "tajweed", "tilawah", "hifz", "hifdh", "muraja", "muraja'a",
#         "tajwid", "qari", "qarie", "quraa", "qurraa", "hafiz", "hafidh", "hafidhul",
#         "surah", "surat", "juz", "ayah", "ayat", "mushaf", "tarteel", "qurani",
#         "qur'anic", "quranic", "suwar", "tafsir", "tilawat", "khatm", "khatmah",
#         "khatmul quran", "quran recitation", "memorization of quran", "quran audio",
#         "quranic verse", "learn quran", "quran learning", "tajweed rules",
#         "tajweed practice", "daily quran", "beautiful recitation", "quran classes",
#         "tajweed course", "memorize quran", "online quran", "quran teacher",
#         "islamic recitation", "islamic audio", "islamic education"
#     ]):
#         return "Quran", "Recitation"

#     # Default fallback
#     else:
#         return "Uncategorized", None
