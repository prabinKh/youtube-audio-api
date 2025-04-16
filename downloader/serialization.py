from rest_framework import serializers
from .models import MediaFile, YouTubeChannel

class YouTubeChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeChannel
        fields = ['id', 'name', 'channel_id', 'created_at']

class MediaFileSerializer(serializers.ModelSerializer):
    youtube_channel = YouTubeChannelSerializer(read_only=True)
    
    class Meta:
        model = MediaFile
        fields = ['id', 'youtube_channel', 'media_url', 'created_at', 'audio_file', 'downloaded_at']
        read_only_fields = ['audio_file', 'downloaded_at']