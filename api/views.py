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


class FetchVideosFromYouTubeAPIView(APIView):
    def get(self, request):
        channel_id = request.GET.get('channel_id')
        max_results = int(request.GET.get('max_results', 5))

        if not channel_id:
            return Response(
                {'error': 'Channel ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            count_saved, video_titles = fetch_videos(channel_id, max_results)
            return Response({
                'message': f'Successfully saved {count_saved} new videos.',
                'videos': video_titles
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# views.py
from rest_framework.generics import ListAPIView

class PendingVideosView(ListAPIView):
    queryset = YouTubeVideo.objects.filter(status='pending')
    serializer_class = YouTubeVideoSerializer




from rest_framework import generics

class ApprovedVideosByCategory(generics.ListAPIView):
    serializer_class = YouTubeVideoSerializer
    pagination_class = StandardResultsSetPagination  # ✅ Add this

    def get_queryset(self):
        queryset = YouTubeVideo.objects.filter(status='approved')  # ✅ Only approved videos
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)  # ✅ Optional filter by category
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

        serializer = YouTubeVideoSerializer(videos, many=True)
        return Response(serializer.data)




class ApproveVideoView(APIView):
    def post(self, request, video_id):
        try:
            video = YouTubeVideo.objects.get(video_id=video_id)
            video.status = 'approved'
            video.save()
            return Response({'message': 'Video approved successfully.'}, status=status.HTTP_200_OK)
        except YouTubeVideo.DoesNotExist:
            return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)




class BulkApproveView(APIView):
    def post(self, request):
        # Approve all videos that are currently in 'pending' status
        updated_count = YouTubeVideo.objects.filter(status='pending').update(status='approved')
        return Response({'message': f'{updated_count} videos approved.'}, status=status.HTTP_200_OK)

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




class ApproveAgainView(APIView):
    def post(self, request, video_id):
        try:
            video = YouTubeVideo.objects.get(video_id=video_id)
            video.status = 'approved'
            video.save()
            return Response({'message': 'Video approved successfully.'}, status=status.HTTP_200_OK)
        except YouTubeVideo.DoesNotExist:
            return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)





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


from django.shortcuts import get_object_or_404

class ApprovedVideoDetailAPIView(APIView):
    def get(self, request, video_id):
        video = get_object_or_404(YouTubeVideo, video_id=video_id, status='approved')
        serializer = YouTubeVideoSerializer(video)
        return Response(serializer.data, status=status.HTTP_200_OK)
