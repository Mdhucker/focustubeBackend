from django.urls import path
from .views import (
    VideoListAPIView, VideoDetailByVideoID, FetchVideosFromYouTubeAPIView, ApprovedVideosByCategory,ApproveVideoView,
    PendingVideosView, SingleVideoAPIView, DustbinVideosByCategory,DeapproveVideoViewOne, BulkApproveView, DeapproveVideoView,
    ApproveAgainView,DeapproveVideoViewOne,ApprovedVideoDetailAPIView
)

urlpatterns = [
    path('pending-videos/', PendingVideosView.as_view(), name='pending-videos'),
    path('videos/<str:video_id>/', SingleVideoAPIView.as_view(), name='video-detail'),
    path('fetch-videos/', FetchVideosFromYouTubeAPIView.as_view(), name='fetch-videos'),
    path('approved/', ApprovedVideosByCategory.as_view(), name='video-list'),
    path('dustbin/', DustbinVideosByCategory.as_view(), name='dustbin-video'),

    path('approve/<str:video_id>/', ApproveVideoView.as_view(), name='approve-video'), #approve the this is in the admin page this button
    path('bulk-approve/', BulkApproveView.as_view(), name='bulk-approve'),  #this also is in the addmin page 
    path('deapprove/<str:video_id>/', DeapproveVideoView.as_view(), name='deapprove-video'),   #this deapprove the  video view in approved page and make remove from the home pg too  

    path('approve_again/<str:video_id>/', ApproveAgainView.as_view(), name='approve-again'),

    path('deapproveone/<str:video_id>/', DeapproveVideoViewOne.as_view(), name='deapprove-video'),
    path('approved/<str:video_id>/', ApprovedVideoDetailAPIView.as_view(), name='approved-video-detail'),
    
    
    ]
    