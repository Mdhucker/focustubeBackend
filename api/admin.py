from django.contrib import admin
from .models import (
    VideoCategory,
    VideoSubCategory,
    VideoTag,
    YouTubeVideo,
    VideoSubCategoryLink,
    VideoTagLink,
    OnlineStatus,
    Message
)


# ─────────────── VideoSubCategory Inline for VideoCategory ───────────────
class VideoSubCategoryInline(admin.TabularInline):
    model = VideoSubCategory
    extra = 1


@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    inlines = [VideoSubCategoryInline]


@admin.register(VideoSubCategory)
class VideoSubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(VideoTag)
class VideoTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


# ─────────────── Inlines for Many-to-Many Linking ───────────────
class VideoSubCategoryLinkInline(admin.TabularInline):
    model = VideoSubCategoryLink
    extra = 1


class VideoTagLinkInline(admin.TabularInline):
    model = VideoTagLink
    extra = 1


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'video_id', 'status', 'gift_status', 'view_count',
        'like_count', 'published_at', 'gift_token', 'subcategory', 'embedding'
    ]
    list_filter = ['status', 'gift_status', 'category', 'subcategory']
    search_fields = ['title', 'video_id', 'channel_title']

    # ✅ Make embedding and fetched_at readonly
    readonly_fields = ['fetched_at', 'embedding']

    inlines = [VideoSubCategoryLinkInline, VideoTagLinkInline]

    fieldsets = (
        (None, {
            'fields': (
                'video_id', 'title', 'description', 'thumbnail_url',
                'published_at', 'channel_title', 'category', 'subcategory',
                'assigned_category', 'duration', 'view_count', 'like_count',
                'comment_count', 'status', 'gift_status', 'gift_token',
                'comment_to_team', 'fetched_at', 'embedding'
            )
        }),
    )


@admin.register(VideoSubCategoryLink)
class VideoSubCategoryLinkAdmin(admin.ModelAdmin):
    list_display = ['video', 'subcategory']
    search_fields = ['video__title', 'subcategory__name']


@admin.register(VideoTagLink)
class VideoTagLinkAdmin(admin.ModelAdmin):
    list_display = ['video', 'tag']
    search_fields = ['video__title', 'tag__name']


@admin.register(OnlineStatus)
class OnlineStatusAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_online', 'last_seen']
    list_filter = ['is_online']
    search_fields = ['user__username']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'text', 'timestamp']
    search_fields = ['sender__username', 'text']
    list_filter = ['timestamp']






# from django.contrib import admin
# from .models import VideoCategory, YouTubeVideo

# @admin.register(VideoCategory)
# class VideoCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     search_fields = ('name',)


# @admin.register(YouTubeVideo)
# class YouTubeVideoAdmin(admin.ModelAdmin):
#     list_display = (
#         'title', 'video_id', 'category', 'assigned_category', 'status',
#         'published_at', 'fetched_at', 'duration',
#         'view_count', 'like_count', 'comment_count'
#     )
#     search_fields = ('title', 'description', 'video_id', 'channel_title', 'assigned_category')
#     list_filter = ('category', 'assigned_category', 'status', 'published_at', 'fetched_at')
#     ordering = ('-published_at',)
#     readonly_fields = ('fetched_at',)
#     list_editable = ('assigned_category', 'status')  # Allows inline editing
