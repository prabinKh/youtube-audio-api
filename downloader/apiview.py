from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import MediaFile, YouTubeChannel
from .serialization import MediaFileSerializer, YouTubeChannelSerializer
from .utils import fetch_and_save_media_urls, check_and_update_media_urls, download_audio

class YouTubeChannelCreateAPIView(generics.CreateAPIView):
    queryset = YouTubeChannel.objects.all()
    serializer_class = YouTubeChannelSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        channel = serializer.save()
        fetch_and_save_media_urls(channel)
        check_and_update_media_urls(repeat=60)
        download_audio(repeat=300)

class ChannelListAPIView(generics.ListAPIView):
    queryset = YouTubeChannel.objects.all()
    serializer_class = YouTubeChannelSerializer
    permission_classes = [IsAuthenticated]

class MediaFileListAPIView(generics.ListAPIView):
    serializer_class = MediaFileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        channel_id = self.kwargs.get('channel_id')
        return MediaFile.objects.filter(youtube_channel_id=channel_id)

class AudioFileListAPIView(generics.ListAPIView):
    queryset = MediaFile.objects.exclude(audio_file='')
    serializer_class = MediaFileSerializer
    permission_classes = [IsAuthenticated]