from rest_framework import serializers
from .models import MediaURL, DownloadedAudio, YouTubeChannel

class YouTubeChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeChannel
        fields = ['id', 'name', 'url', 'channel_id', 'created_at']
        extra_kwargs = {
            'url': {'required': False, 'allow_blank': True},  # Make URL optional
            'channel_id': {'read_only': True},
            'created_at': {'read_only': True},
        }

class MediaURLSerializer(serializers.ModelSerializer):
    youtube_channel = YouTubeChannelSerializer(read_only=True)
    youtube_channel_id = serializers.PrimaryKeyRelatedField(
        write_only=True, 
        queryset=YouTubeChannel.objects.all(),
        source='youtube_channel'
    )
    
    class Meta:
        model = MediaURL
        fields = ['id', 'youtube_channel', 'youtube_channel_id', 'media_url', 'created_at']

class DownloadedAudioSerializer(serializers.ModelSerializer):
    media_url = MediaURLSerializer(read_only=True)
    
    class Meta:
        model = DownloadedAudio
        fields = ['id', 'media_url', 'audio_file', 'downloaded_at']