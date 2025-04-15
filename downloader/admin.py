from django.contrib import admin
from .models import YouTubeChannel, MediaURL, DownloadedAudio


class DownloadedAudioInline(admin.TabularInline):
    model = DownloadedAudio
    extra = 0


class MediaURLInline(admin.TabularInline):
    model = MediaURL
    extra = 0


@admin.register(YouTubeChannel)
class YouTubeChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel_id', 'url', 'created_at')
    inlines = [MediaURLInline]


@admin.register(MediaURL)
class MediaURLAdmin(admin.ModelAdmin):
    list_display = ('media_url', 'youtube_channel', 'created_at')
    inlines = [DownloadedAudioInline]


@admin.register(DownloadedAudio)
class DownloadedAudioAdmin(admin.ModelAdmin):
    list_display = ('media_url', 'audio_file', 'downloaded_at')
