from django.db import models

class VideoCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class YouTubeVideo(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('dustbin', 'Dustbin'),
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
    assigned_category = models.CharField(max_length=100, blank=True, null=True)  # Manual override

    duration = models.CharField(max_length=20)  # ISO 8601 e.g. "PT10M30S"
    view_count = models.BigIntegerField(default=0)
    like_count = models.BigIntegerField(default=0)
    comment_count = models.BigIntegerField(default=0)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
    )

    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.video_id})"

    class Meta:
        ordering = ['-published_at']
        verbose_name = "YouTube Video"
        verbose_name_plural = "YouTube Videos"
