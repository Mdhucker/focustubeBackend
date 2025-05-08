from rest_framework import serializers
from .models import YouTubeVideo

# serializers.py
from rest_framework import serializers
from .models import YouTubeVideo

CATEGORY_MAPPING = {
    '1': 'Film & Animation',
    '2': 'Autos & Vehicles',
    '10': 'Music',
    '15': 'Pets & Animals',
    '17': 'Sports',
    '18': 'Short Movies',
    '19': 'Travel & Events',
    '20': 'Gaming',
    '21': 'Videoblogging',
    '22': 'People & Blogs',
    '23': 'Comedy',
    '24': 'Entertainment',
    '25': 'News & Politics',
    '26': 'Howto & Style',
    '27': 'Education',
    '28': 'Science & Technology',
    '29': 'Nonprofits & Activism',
    '30': 'Movies',
    '31': 'Anime/Animation',
    '32': 'Action/Adventure',
    '33': 'Classics',
    '34': 'Comedy',
    '35': 'Documentary',
    '36': 'Drama',
    '37': 'Family',
    '38': 'Foreign',
    '39': 'Horror',
    '40': 'Sci-Fi/Fantasy',
    '41': 'Thriller',
    '42': 'Shorts',
    '43': 'Shows',
    '44': 'Trailers',
}

class YouTubeVideoSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = YouTubeVideo
        fields = '__all__'  # or list them manually
        # Add 'category_name' to the fields if listing manually

    def get_category_name(self, obj):
        return CATEGORY_MAPPING.get(str(obj.categoryId), 'Uncategorized')




class YouTubeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeVideo
        fields = '__all__'



# from rest_framework import serializers
# from .models import YouTubeVideo, VideoCategory

# CATEGORY_MAPPING = {
#     '1': 'Film & Animation',
#     '2': 'Autos & Vehicles',
#     '10': 'Music',
#     '15': 'Pets & Animals',
#     '17': 'Sports',
#     '18': 'Short Movies',
#     '19': 'Travel & Events',
#     '20': 'Gaming',
#     '21': 'Videoblogging',
#     '22': 'People & Blogs',
#     '23': 'Comedy',
#     '24': 'Entertainment',
#     '25': 'News & Politics',
#     '26': 'Howto & Style',
#     '27': 'Education',
#     '28': 'Science & Technology',
#     '29': 'Nonprofits & Activism',
#     '30': 'Movies',
#     '31': 'Anime/Animation',
#     '32': 'Action/Adventure',
#     '33': 'Classics',
#     '34': 'Comedy',
#     '35': 'Documentary',
#     '36': 'Drama',
#     '37': 'Family',
#     '38': 'Foreign',
#     '39': 'Horror',
#     '40': 'Sci-Fi/Fantasy',
#     '41': 'Thriller',
#     '42': 'Shorts',
#     '43': 'Shows',
#     '44': 'Trailers',
# }

# class VideoCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VideoCategory
#         fields = ['id', 'name']


# class YouTubeVideoSerializer(serializers.ModelSerializer):
#     category = VideoCategorySerializer(read_only=True)
#     category_id = serializers.PrimaryKeyRelatedField(
#         queryset=VideoCategory.objects.all(),
#         source='category',
#         write_only=True,
#         required=False
#     )
#     category_name = serializers.SerializerMethodField()

#     class Meta:
#         model = YouTubeVideo
#         fields = '__all__'  # Includes everything including status, video_id, etc.

#     def get_category_name(self, obj):
#         if obj.category:
#             return obj.category.name
#         # Fallback to assigned category name if available
#         if obj.assigned_category:
#             return obj.assigned_category
#         # Fallback to YouTube’s default category mapping using video.categoryId
#         return CATEGORY_MAPPING.get(str(getattr(obj, "categoryId", "")), "Uncategorized")
