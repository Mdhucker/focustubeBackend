from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
from .models import YouTubeVideo
from .serializers import YouTubeVideoSerializer
from .utils.fetch_youtube_videos import fetch_videos
from rest_framework.generics import ListAPIView
from .models import YouTubeVideo
from .serializers import YouTubeVideoSerializer
from .pagination import StandardResultsSetPagination  # ✅ import here
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class VideoListAPIView(APIView):
    def get(self, request):
        videos = YouTubeVideo.objects.all().order_by('-published_at')
        serializer = YouTubeVideoSerializer(videos, many=True)
        pagination_class = StandardResultsSetPagination   # ✅ import here

        return Response(serializer.data)


class VideoDetailByVideoID(APIView):
    def get(self, request, video_id):
        try:
            video = YouTubeVideo.objects.get(video_id=video_id)
            serializer = YouTubeVideoSerializer(video)
            return Response(serializer.data)
        except YouTubeVideo.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)


import traceback
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# from .youtube_fetcher import fetch_videos, fetch_videos_from_channel
from .utils.fetch_youtube_videos import fetch_videos_from_channel

class FetchVideosFromYouTubeAPIView(APIView):
    def get(self, request):
        channel_id = request.GET.get('channel_id')
        max_results = int(request.GET.get('max_results', 5))

        try:
            if channel_id:
                count_saved, video_titles = fetch_videos_from_channel(channel_id, max_results)
            else:
                count_saved, video_titles = fetch_videos(None, max_results)

            return Response({
                'message': f'Successfully saved {count_saved} new videos.',
                'videos': video_titles
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("❌ Error during fetch_videos:", str(e))
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# your_app/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ExtractChannelIDView(APIView):
    """
    GET /api/extract-channel-id/?url=https://youtube.com/channel/CHANNEL_ID
    """

    def get(self, request):
        youtube_url = request.GET.get('url')

        if not youtube_url:
            return Response(
                {'error': 'YouTube URL parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        channel_id = extract_channel_id(youtube_url)

        if channel_id:
            return Response({'channel_id': channel_id}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid YouTube URL. Format must be https://youtube.com/channel/<channel_id>'},
                status=status.HTTP_400_BAD_REQUEST
            )


from .utils.fetch_youtube_videos import get_channel_id_from_video_id

class ResolveChannelIdFromVideo(APIView):
    def get(self, request, *args, **kwargs):
        video_id = request.GET.get('video_id')

        if not video_id:
            return Response({"error": "Video ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            channel_id = get_channel_id_from_video_id(video_id)
            if channel_id:
                return Response({"channel_id": channel_id}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Channel ID could not be resolved."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# views.py
from rest_framework.generics import ListAPIView

class PendingVideosView(ListAPIView):
    queryset = YouTubeVideo.objects.filter(status='pending')
    serializer_class = YouTubeVideoSerializer



from rest_framework import generics
from .models import YouTubeVideo
from .serializers import YouTubeVideoSerializer
from .pagination import StandardResultsSetPagination
class ApprovedVideosByCategory(generics.ListAPIView):
    serializer_class = YouTubeVideoSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = YouTubeVideo.objects.filter(status='approved')

        # Multiple categories: e.g., ?categories=Mindset,War,Languages
        categories_param = self.request.query_params.get('categories')
        if categories_param:
            category_names = [cat.strip().title() for cat in categories_param.split(',')]
            queryset = queryset.filter(category__name__in=category_names)

        # Optional: Filter by subcategory name or ID
        subcategory_name = self.request.query_params.get('subcategory')
        subcategory_id = self.request.query_params.get('subcategory_id')

        if subcategory_name:
            queryset = queryset.filter(subcategory__name__iexact=subcategory_name)
        elif subcategory_id:
            queryset = queryset.filter(subcategory__id=subcategory_id)

        return queryset



class SingleVideoAPIView(generics.RetrieveAPIView):
    serializer_class = YouTubeVideoSerializer
    lookup_field = 'video_id'

    def get_queryset(self):
        return YouTubeVideo.objects.all()




# views.py


from rest_framework.permissions import AllowAny

class DustbinVideosByCategory(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        category = request.query_params.get('category', None)
        if category:
            videos = YouTubeVideo.objects.filter(status='dustbin', assigned_category__iexact=category)
        else:
            videos = YouTubeVideo.objects.filter(status='dustbin')
        pagination_class = StandardResultsSetPagination  # ✅ Add this

        serializer = YouTubeVideoSerializer(videos, many=True)
        
        return Response(serializer.data)




# class ApproveVideoView(APIView):
#     def post(self, request, video_id):
#         try:
#             video = YouTubeVideo.objects.get(video_id=video_id)
#             video.status = 'approved'
#             video.save()
#             return Response({'message': 'Video approved successfully.'}, status=status.HTTP_200_OK)
#         except YouTubeVideo.DoesNotExist:
#             return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import YouTubeVideo
from .vector_utils import save_embedding_to_faiss
import numpy as np

class ApproveVideoView(APIView):
    def post(self, request, video_id):
        try:
            video = YouTubeVideo.objects.get(video_id=video_id)

            video.status = 'approved'

            # 🔹 Create embedding from title + description
            content = f"{video.title}\n{video.description}"
            embedding = get_embedding(content)

            # 🔹 Convert to binary for saving in BinaryField
            video.embedding = np.array(embedding, dtype=np.float32).tobytes()

            video.save()

            return Response({'message': 'Video approved successfully.'}, status=status.HTTP_200_OK)

        except YouTubeVideo.DoesNotExist:
            return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)




# class BulkApproveView(APIView):
#     def post(self, request):
#         # Approve all videos that are currently in 'pending' status
#         updated_count = YouTubeVideo.objects.filter(status='pending').update(status='approved')
#         return Response({'message': f'{updated_count} videos approved.'}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import YouTubeVideo
from api.vector_utils import get_embedding, save_embedding_to_faiss
import numpy as np
import re

class BulkApproveView(APIView):
    def post(self, request):
        # Get all pending videos
        pending_videos = list(YouTubeVideo.objects.filter(status='pending'))
        updated_count = 0
        embedded_count = 0
        failed_videos = []

        for video in pending_videos:
            try:
                # Clean and combine text
                text = f"{video.title} {video.description or ''}"
                text = re.sub(r'\s+', ' ', text.strip())

                # Get embedding
                embedding = get_embedding(text)
                if embedding is None:
                    raise ValueError("Empty embedding")

                # Convert to NumPy and store
                embedding = np.array(embedding, dtype=np.float32)
                video.embedding = embedding.tobytes()
                video.status = 'approved'
                video.save()
                embedded_count += 1

                # Save to FAISS
                save_embedding_to_faiss(
                    video_id=video.video_id,
                    embedding=embedding,
                    metadata={
                        "video_id": video.video_id,
                        "title": video.title,
                        "category": str(video.category.name if video.category else ""),
                        "subcategory": str(video.subcategory.name if video.subcategory else ""),
                        "created_at": str(video.created_at) if hasattr(video, "created_at") else "",
                        "views": int(getattr(video, "view_count", 0)),
                    }
                )

                updated_count += 1

            except Exception as e:
                print(f"❌ Failed to embed/save video {video.video_id}: {e}")
                failed_videos.append(video.video_id)

        return Response({
            'message': f'{updated_count} videos approved and embedded.',
            'successful': embedded_count,
            'failed': failed_videos
        }, status=status.HTTP_200_OK)

# views.py

from rest_framework import status as http_status

class DeapproveVideoView(APIView):
    def post(self, request, video_id):
        try:
            video = YouTubeVideo.objects.get(video_id=video_id)
            if video.status == 'approved':
                video.status = 'dustbin'
                video.save()
                return Response({'message': 'Video moved to dustbin.'}, status=http_status.HTTP_200_OK)
            else:
                return Response({'message': 'Video is not approved.'}, status=http_status.HTTP_400_BAD_REQUEST)
        except YouTubeVideo.DoesNotExist:
            return Response({'error': 'Video not found.'}, status=http_status.HTTP_404_NOT_FOUND)




# class ApproveAgainView(APIView):
#     def post(self, request, video_id):
#         try:
#             video = YouTubeVideo.objects.get(video_id=video_id)
#             video.status = 'approved'
#             video.save()
#             return Response({'message': 'Video approved successfully.'}, status=status.HTTP_200_OK)
#         except YouTubeVideo.DoesNotExist:
#             return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import YouTubeVideo
from transformers import AutoTokenizer, AutoModel
from .vector_utils import get_embedding, save_embedding_to_faiss
class ApproveAgainView(APIView):
    def post(self, request, video_id):
        try:
            video = YouTubeVideo.objects.get(video_id=video_id)

            # Clean and combine text
            text = f"{video.title} {video.description}"
            text = re.sub(r'\s+', ' ', text.strip())

            embedding = get_embedding(text)

            if embedding is None:
                return Response({'error': 'Embedding failed, text is empty.'}, status=status.HTTP_400_BAD_REQUEST)

            # Convert to NumPy and store in model
            embedding = np.array(embedding, dtype=np.float32)
            video.embedding = embedding.tobytes()  # ✅ safe now
            video.status = 'approved'
            video.save()

            # Save to FAISS
            save_embedding_to_faiss(
                video_id=video.video_id,
                embedding=embedding,
                metadata={
                    "video_id": video.video_id,
                    "title": video.title,
                    "category": str(video.category.name if video.category else ""),
                    "subcategory": str(video.subcategory.name if video.subcategory else ""),
                    "created_at": str(video.created_at) if hasattr(video, "created_at") else "",
                    "views": int(getattr(video, "view_count", 0)),
                }
            )

            return Response({'message': 'Video approved and saved to vector DB successfully.'}, status=status.HTTP_200_OK)

        except YouTubeVideo.DoesNotExist:
            return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeapproveVideoViewOne(APIView):
    def post(self, request, video_id):
        try:
            video = YouTubeVideo.objects.get(video_id=video_id)
            video.status = 'dustbin'  # or 'deapproved' depending on your design
            video.save()
            return Response({"message": "Video deapproved successfully."}, status=status.HTTP_200_OK)
        except YouTubeVideo.DoesNotExist:
            return Response({"error": "Video not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#this is for waching page function 
class ApprovedVideoDetailAPIView(APIView):
    def get(self, request, video_id):
        video = get_object_or_404(YouTubeVideo, video_id=video_id, status='approved')  
        serializer = YouTubeVideoSerializer(video)
        return Response(serializer.data, status=status.HTTP_200_OK)


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db.models import Q
# from .models import YouTubeVideo
# from rest_framework.decorators import api_view
# class VideoSuggestionsAPIView(APIView):
#     def get(self, request, *args, **kwargs):
#         query = request.GET.get('query', '').strip()

#         # If the query is empty, return history suggestions if available (otherwise return empty list)
#         if not query:
#             # Get historical search terms from the user's session or database (for example)
#             history_suggestions = request.session.get('search_history', [])  # Assuming history is stored in session
#             if history_suggestions:
#                 return Response(history_suggestions, status=status.HTTP_200_OK)
#             else:
#                 return Response([], status=status.HTTP_200_OK)

#         # If query is provided, filter based on the query
#         suggestions = YouTubeVideo.objects.filter(
#             Q(title__icontains=query),
#             status='approved'
#         ).values('title', 'description')[:10]

#         return Response(list(suggestions), status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import YouTubeVideo
from rest_framework.decorators import api_view

class VideoSuggestionsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '').strip()

        # If the query is empty, return history suggestions if available (otherwise return empty list)
        if not query:
            # Get historical search terms from the user's session or database (for example)
            history_suggestions = request.session.get('search_history', [])  # Assuming history is stored in session
            if history_suggestions:
                return Response(history_suggestions, status=status.HTTP_200_OK)
            else:
                return Response([], status=status.HTTP_200_OK)

        # If query is provided, filter based on the query
        suggestions = YouTubeVideo.objects.filter(
            Q(title__icontains=query),
            status='approved'
        ).values('id', 'title', 'description')[:10]  # Include 'id' for clickable links

        return Response(list(suggestions), status=status.HTTP_200_OK)



from rest_framework.generics import RetrieveAPIView
from .models import YouTubeVideo
from .serializers import YouTubeVideoSerializer

class VideoDetailAPIView(RetrieveAPIView):
    queryset = YouTubeVideo.objects.filter(status='approved')
    serializer_class = YouTubeVideoSerializer



class GiftAllPendingAPIView(APIView):
    def get(self, request, *args, **kwargs):
        pending_videos = YouTubeVideo.objects.filter(status='pending')
        count = pending_videos.count()

        if count == 0:
            return Response({"message": "No pending videos to gift."}, status=status.HTTP_200_OK)

        # Store the videos about to be gifted
        gifted_video_ids = list(pending_videos.values_list('id', flat=True))

        # Perform update
        pending_videos.update(status='gift')

        # Retrieve only the newly gifted videos
        gifted_videos = YouTubeVideo.objects.filter(id__in=gifted_video_ids)
        serializer = YouTubeVideoSerializer(gifted_videos, many=True)

        return Response({
            'message': f'{count} pending video(s) have been gifted.',
            'gifted': serializer.data
        }, status=status.HTTP_200_OK)


class GiftAllPendingAPIView(APIView):
    def get(self, request, *args, **kwargs):
        gifted_videos = YouTubeVideo.objects.filter(status='gift')
        serializer = YouTubeVideoSerializer(gifted_videos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





class AssignGiftTokenAPIView(APIView):
    def patch(self, request, pk):
        token = request.data.get("gift_token")
        if not token:
            return Response({"error": "Gift token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = YouTubeVideo.objects.get(pk=pk)
        except YouTubeVideo.DoesNotExist:
            return Response({"error": "Video not found."}, status=status.HTTP_404_NOT_FOUND)

        video.gift_token = token
        video.gift_status = True
        video.status = 'gift'
        video.save()

        return Response({"message": "Gift token assigned successfully."}, status=status.HTTP_200_OK)




from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomEmailTokenObtainPairSerializer

class CustomEmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomEmailTokenObtainPairSerializer



from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from django.contrib.auth.models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)


from rest_framework.generics import CreateAPIView
from .serializers import RegisterSerializer
from django.contrib.auth.models import User

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        # Use username internally for JWT
        data = super().validate({
            'username': user.username,
            'password': password
        })

        # Add extra info if needed
        data["username"] = user.username
        data["email"] = user.email
        return data


from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer

class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# from api.utils.fetch_single_video import fetch_single_video  # 👈 ADD THIS HERE

# from api.utils.fetch_single_video import fetch_single_video
from rest_framework.response import Response

class FetchVideoAPI(APIView):
    def post(self, request):
        video_id = request.data.get("video_id")
        success, message = fetch_and_save_video(video_id)
        return Response({"success": success, "message": message})

# your_app/views.py
# views.py
# views.py
import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .llama_router import recommend_best_video
from .models import YouTubeVideo
@method_decorator(csrf_exempt, name='dispatch')

@method_decorator(csrf_exempt, name='dispatch')
class LlamaChatView(View):
    def get(self, request):
        query = request.GET.get("query", "").strip()
        if not query:
            return JsonResponse({"error": "Missing query"}, status=400)
        return self.handle_query(query)

    def post(self, request):
        try:
            body = json.loads(request.body)
            query = body.get("message", "").strip()
            if not query:
                return JsonResponse({"error": "Empty message"}, status=400)
            return self.handle_query(query)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    def handle_query(self, user_message):
        gpt_response = recommend_best_video(user_message)
        keywords = user_message.lower().split()
        search_filter = Q()
        for word in keywords:
            search_filter |= Q(title__icontains=word) | Q(description__icontains=word)

        matched_videos = YouTubeVideo.objects.filter(search_filter).values(
            "id", "title", "description", "video_id","thumbnail_url"
        )[:7]

        videos = []
        for v in matched_videos:
            videos.append(v)

        return JsonResponse({
            "response": gpt_response,
            "videos": videos
        }, status=200)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import YouTubeVideoSerializer
from api.search import search_similar_videos  # ← ✅ Add this!

class SemanticVideoSearchView(APIView):
    def get(self, request):
        query = request.GET.get('query')
        if not query:
            return Response({'error': 'Query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = search_similar_videos(query)
        serializer = YouTubeVideoSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
