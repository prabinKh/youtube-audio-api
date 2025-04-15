# yourapp/models.py

from django.db import models

class YouTubeChannel(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    channel_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.channel_id})"

class MediaURL(models.Model):
    youtube_channel = models.ForeignKey(YouTubeChannel, on_delete=models.CASCADE, related_name='media_urls')
    media_url = models.URLField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.media_url
class DownloadedAudio(models.Model):
    media_url = models.ForeignKey(MediaURL, on_delete=models.CASCADE, related_name='downloaded_audio')
    audio_file = models.FileField(upload_to='audio/')  # Path where the audio file is stored
    downloaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Audio for {self.media_url.media_url}"
    
