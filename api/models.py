from django.db import models
from django.contrib.auth.models import User

# ─────────────── Category ───────────────

class VideoCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ─────────────── Subcategory ───────────────

class VideoSubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return f"{self.name} ({self.category.name})"


# ─────────────── Tag ───────────────

class VideoTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# ─────────────── Main Video Model ───────────────

# class YouTubeVideo(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('dustbin', 'Dustbin'),
#         ('gift','Gift'),
#     ]

#     video_id = models.CharField(max_length=20, unique=True)  # YouTube video ID
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     thumbnail_url = models.URLField()
#     published_at = models.DateTimeField()
#     channel_title = models.CharField(max_length=255, blank=True, null=True)
#     category = models.ForeignKey(
#         VideoCategory,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="videos"
#     )
#     assigned_category = models.CharField(max_length=100, blank=True, null=True)  # Manual override
#     subcategory = models.ForeignKey(VideoSubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
#     duration = models.CharField(max_length=20)  # ISO 8601 e.g. "PT10M30S"
#     view_count = models.BigIntegerField(default=0)
#     like_count = models.BigIntegerField(default=0)
#     comment_count = models.BigIntegerField(default=0)

#     status = models.CharField(
#         max_length=10,
#         choices=STATUS_CHOICES,
#         default='pending',
#     )

#     gift_status = models.BooleanField(default=False)  # 🎁 New field for marking gifts
#     gift_token = models.CharField(max_length=100, blank=True, null=True)  # 🌟 Add this
#     comment_to_team = models.TextField(blank=True, null=True)  # 💬 New internal team comment field

#     fetched_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.title} ({self.video_id})"

#     class Meta:
#         ordering = ['-published_at']
#         verbose_name = "YouTube Video"
#         verbose_name_plural = "YouTube Videos"


# models.py
class YouTubeVideo(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('dustbin', 'Dustbin'),
        ('gift','Gift'),
    ]

    video_id = models.CharField(max_length=20, unique=True)  # YouTube video ID
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    thumbnail_url = models.URLField()
    published_at = models.DateTimeField()
    channel_title = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(
        VideoCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="videos"
    )
    embedding = models.BinaryField(blank=True, null=True)  # Store vector as bytes
    assigned_category = models.CharField(max_length=100, blank=True, null=True)  # Manual override
    subcategory = models.ForeignKey(VideoSubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    # slug = models.SlugField(unique=True, blank=True, null=True)  # <-- Is this present?

    duration = models.CharField(max_length=20)  # ISO 8601 e.g. "PT10M30S"
    view_count = models.BigIntegerField(default=0)
    like_count = models.BigIntegerField(default=0)
    comment_count = models.BigIntegerField(default=0)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
    )

    gift_status = models.BooleanField(default=False)  # 🎁 New field for marking gifts
    gift_token = models.CharField(max_length=100, blank=True, null=True)  # 🌟 Add this
    comment_to_team = models.TextField(blank=True, null=True)  # 💬 New internal team comment field

    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.video_id})"

    class Meta:
        ordering = ['-published_at']
        verbose_name = "YouTube Video"
        verbose_name_plural = "YouTube Videos"


# ─────────────── Linking Models ───────────────

class VideoSubCategoryLink(models.Model):
    video = models.ForeignKey(YouTubeVideo, on_delete=models.CASCADE, related_name='subcategory_links')
    subcategory = models.ForeignKey(
    VideoSubCategory,
    on_delete=models.CASCADE,
    related_name='video_links',
    null=True,
    blank=True  # <-- required for forms/admin to work too
)

    # subcategory = models.ForeignKey(VideoSubCategory, on_delete=models.CASCADE, related_name='video_links')

    class Meta:
        unique_together = ('video', 'subcategory')


class VideoTagLink(models.Model):
    video = models.ForeignKey(YouTubeVideo, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(VideoTag, on_delete=models.CASCADE, related_name='videos')

    class Meta:
        unique_together = ('video', 'tag')


# ─────────────── Chat and User Online Tracking ───────────────

class OnlineStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.text[:30]}"














# from django.db import models

# class VideoCategory(models.Model):
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name


# class YouTubeVideo(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('dustbin', 'Dustbin'),
#     ]

#     video_id = models.CharField(max_length=20, unique=True)  # YouTube video ID
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     thumbnail_url = models.URLField()
#     published_at = models.DateTimeField()
#     channel_title = models.CharField(max_length=255, blank=True, null=True)
#     category = models.ForeignKey(
#         VideoCategory,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="videos"
#     )
#     assigned_category = models.CharField(max_length=100, blank=True, null=True)  # Manual override

#     duration = models.CharField(max_length=20)  # ISO 8601 e.g. "PT10M30S"
#     view_count = models.BigIntegerField(default=0)
#     like_count = models.BigIntegerField(default=0)
#     comment_count = models.BigIntegerField(default=0)

#     status = models.CharField(
#         max_length=10,
#         choices=STATUS_CHOICES,
#         default='pending',
#     )

#     fetched_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.title} ({self.video_id})"

#     class Meta:
#         ordering = ['-published_at']
#         verbose_name = "YouTube Video"
#         verbose_name_plural = "YouTube Videos"
