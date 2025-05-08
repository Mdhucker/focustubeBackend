from django.contrib import admin
from .models import VideoCategory, YouTubeVideo

@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'video_id', 'category', 'assigned_category', 'status',
        'published_at', 'fetched_at', 'duration',
        'view_count', 'like_count', 'comment_count'
    )
    search_fields = ('title', 'description', 'video_id', 'channel_title', 'assigned_category')
    list_filter = ('category', 'assigned_category', 'status', 'published_at', 'fetched_at')
    ordering = ('-published_at',)
    readonly_fields = ('fetched_at',)
    list_editable = ('assigned_category', 'status')  # Allows inline editing
