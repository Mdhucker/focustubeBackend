from django.urls import path
from .views import (
    VideoListAPIView, VideoDetailByVideoID, FetchVideosFromYouTubeAPIView, ApprovedVideosByCategory,ApproveVideoView,
    PendingVideosView, SingleVideoAPIView, DustbinVideosByCategory,DeapproveVideoViewOne, BulkApproveView, DeapproveVideoView,
    ApproveAgainView,DeapproveVideoViewOne,ApprovedVideoDetailAPIView,VideoSuggestionsAPIView,VideoDetailAPIView,
    GiftAllPendingAPIView,AssignGiftTokenAPIView,CustomEmailTokenObtainPairView,RegisterView,
    CurrentUserAPIView,ExtractChannelIDView,ResolveChannelIdFromVideo, FetchVideoAPI,LlamaChatView, SemanticVideoSearchView
)

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 


urlpatterns = [
    path('pending-videos/', PendingVideosView.as_view(), name='pending-videos'),
    path('videos/<str:video_id>/', SingleVideoAPIView.as_view(), name='video-detail'),
    path('fetch-videos/', FetchVideosFromYouTubeAPIView.as_view(), name='fetch-videos'),
    path('extract-channel-id/', ExtractChannelIDView.as_view(), name='extract-channel-id'),
    path('resolve-channel-id-from-video/', ResolveChannelIdFromVideo.as_view(), name='resolve-channel-id'),

    path('approved/', ApprovedVideosByCategory.as_view(), name='video-list'),   #this is approved for home page not for anything else 
    path('dustbin/', DustbinVideosByCategory.as_view(), name='dustbin-video'),

    path('approve/<str:video_id>/', ApproveVideoView.as_view(), name='approve-video'), #approve the this is in the admin page this button
    path('bulk-approve/', BulkApproveView.as_view(), name='bulk-approve'),  #this also is in the addmin page 
    path('deapprove/<str:video_id>/', DeapproveVideoView.as_view(), name='deapprove-video'),   #this deapprove the  video view in approved page and make remove from the home pg too  

    path('approve_again/<str:video_id>/', ApproveAgainView.as_view(), name='approve-again'),

    path('deapproveone/<str:video_id>/', DeapproveVideoViewOne.as_view(), name='deapprove-video'),
    path('approved/<str:video_id>/', ApprovedVideoDetailAPIView.as_view(), name='approved-video-detail'),
    
    path('suggestions/', VideoSuggestionsAPIView.as_view(), name='video_suggestions'),

    path('videos_input/<int:pk>/', VideoDetailAPIView.as_view(), name='video-detail'),



    path('gift-all/', GiftAllPendingAPIView.as_view(), name='gift-all'),

    path('assign-gift/<int:pk>/', AssignGiftTokenAPIView.as_view(), name='assign-gift'),   
    


    path('register/', RegisterView.as_view(), name='register'),
        path('login/', CustomEmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', CurrentUserAPIView.as_view(), name='current-user'),    
    #  path('', YouTubeVideoCreateView.as_view(), name='youtube-video-create'),
    path('youtube-videos/', FetchVideoAPI.as_view(), name='youtube-video-create'),


    # path("deepseek-chat/", DeepSeekChatView.as_view(), name="deepseek_chat"),
    # path('recommend/', RecommendTopicView.as_view(), name="deepseek_recommendation"),
    # path("recommendations/", RecommendTopicView.as_view(), name="recommend-topic"),
    # path('llama-chat/', LlamaChatView.as_view(), name='llama_chat'),
    path("recommend/", LlamaChatView.as_view(), name="recommend_video"),
    path('search/', SemanticVideoSearchView.as_view(), name='semantic_video_search'),

       ]
    
