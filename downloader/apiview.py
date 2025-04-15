from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import MediaURL, DownloadedAudio, YouTubeChannel
from .serialization import MediaURLSerializer, DownloadedAudioSerializer, YouTubeChannelSerializer  # Updated import
from .utils import fetch_and_save_media_urls, check_and_update_media_urls, download_audio

class YouTubeChannelCreateAPIView(generics.CreateAPIView):
    queryset = YouTubeChannel.objects.all()
    serializer_class = YouTubeChannelSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        channel = serializer.save()
        fetch_and_save_media_urls(channel)
        check_and_update_media_urls(repeat=60)  # Every minute
        download_audio(repeat=300)  # Every 5 minutes

class MediaURLListCreateAPIView(generics.ListCreateAPIView):
    queryset = MediaURL.objects.all()
    serializer_class = MediaURLSerializer
    permission_classes = [IsAuthenticated]

class MediaURLDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MediaURL.objects.all()
    serializer_class = MediaURLSerializer
    permission_classes = [IsAuthenticated]

class DownloadedAudioListAPIView(generics.ListAPIView):
    queryset = DownloadedAudio.objects.all()
    serializer_class = DownloadedAudioSerializer
    permission_classes = [IsAuthenticated]

class DownloadedAudioDetailAPIView(generics.RetrieveAPIView):
    queryset = DownloadedAudio.objects.all()
    serializer_class = DownloadedAudioSerializer
    permission_classes = [IsAuthenticated]