from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import YouTubeChannel, MediaURL, DownloadedAudio
from .forms import YouTubeChannelForm
from .utils import fetch_and_save_media_urls, check_and_update_media_urls, download_audio
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

def custom_logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')

@login_required
def channel_list(request):
    channels = YouTubeChannel.objects.all()
    return render(request, 'downloader/channel_list.html', {'channels': channels})

@login_required
def add_channel(request):
    if request.method == 'POST':
        form = YouTubeChannelForm(request.POST)
        if form.is_valid():
            channel = form.save()
            fetch_and_save_media_urls(channel)
            
            # Schedule background tasks if they're not already scheduled
            check_and_update_media_urls(repeat=60)  # Schedule to run every minute
            download_audio(repeat=300)  # Schedule to run every 5 minutes
            
            return redirect('channel_list') 
    else:
        form = YouTubeChannelForm()
    return render(request, 'downloader/add_channel.html', {'form': form})

@login_required
def media_list(request, channel_id):
    channel = YouTubeChannel.objects.get(id=channel_id)
    media_urls = channel.media_urls.all()
    return render(request, 'downloader/media_list.html', {
        'channel': channel,
        'media_urls': media_urls
    })

@login_required
def audio_list(request):
    audio_files = DownloadedAudio.objects.all().order_by('-downloaded_at')
    return render(request, 'downloader/audio_list.html', {
        'audio_files': audio_files
    })