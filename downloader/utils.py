import os
import re
import subprocess
import xml.etree.ElementTree as ET

import requests
from background_task import background
from django.conf import settings
from django.core.files import File
from django.utils import timezone

from .models import YouTubeChannel, MediaFile

def fetch_and_save_media_urls(youtube_channel):
    """Fetch media URLs from YouTube channel RSS feed."""
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={youtube_channel.channel_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(rss_url, headers=headers)
        root = ET.fromstring(response.content)

        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "media": "http://search.yahoo.com/mrss/",
            "yt": "http://www.youtube.com/xml/schemas/2015",
        }

        for entry in root.findall("atom:entry", ns):
            media_content = entry.find("media:group/media:content", ns)
            if media_content is not None:
                url = media_content.attrib.get("url")
                if url and not MediaFile.objects.filter(media_url=url).exists():
                    MediaFile.objects.create(
                        youtube_channel=youtube_channel,
                        media_url=url,
                        created_at=timezone.now(),
                    )
                    print(f"✅ New media URL saved: {url}")
    except Exception as e:
        print(f"❌ Error fetching RSS: {e}")

@background(schedule=1)  # Run every 60 seconds
def check_and_update_media_urls():
    """Background task to check and update media URLs for all YouTube channels."""
    youtube_channels = YouTubeChannel.objects.all()

    for youtube_channel in youtube_channels:
        print(f"Checking updates for YouTube Channel: {youtube_channel.name} ({youtube_channel.channel_id})")
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={youtube_channel.channel_id}"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(rss_url, headers=headers)
            response.raise_for_status()
            root = ET.fromstring(response.content)

            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "media": "http://search.yahoo.com/mrss/",
                "yt": "http://www.youtube.com/xml/schemas/2015",
            }

            existing_urls = set(
                MediaFile.objects.filter(youtube_channel=youtube_channel).values_list(
                    "media_url", flat=True
                )
            )

            for entry in root.findall("atom:entry", ns):
                media_content = entry.find("media:group/media:content", ns)
                if media_content is not None:
                    url = media_content.attrib.get("url")
                    if url and url not in existing_urls:
                        MediaFile.objects.create(
                            youtube_channel=youtube_channel,
                            media_url=url,
                            created_at=timezone.now(),
                        )
                        print(f"✅ New media URL added: {url}")
                        existing_urls.add(url)

        except Exception as e:
            print(f"❌ Error fetching RSS for {youtube_channel.name}: {e}")

@background(schedule=3)  # Run every 5 minutes
def download_audio():
    """Background task to download audio from YouTube URLs."""
    audio_dir = os.path.join(settings.MEDIA_ROOT, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    media_files = MediaFile.objects.filter(audio_file='')

    if media_files.exists():
        for media in media_files:
            url = media.media_url

            try:
                filename = f"{media.youtube_channel.channel_id}_{media.id}"
                filename = re.sub(r"[^a-zA-Z0-9_-]", "_", filename)

                output_template = os.path.join(audio_dir, f"{filename}.%(ext)s")
                absolute_audio_path = os.path.join(audio_dir, f"{filename}.mp3")

                command = [
                    "yt-dlp",
                    "-x",
                    "--audio-format",
                    "mp3",
                    "--audio-quality",
                    "0",
                    "--output",
                    output_template,
                    url,
                ]

                subprocess.run(command, check=True)

                if os.path.exists(absolute_audio_path):
                    with open(absolute_audio_path, "rb") as audio_file:
                        media.audio_file = File(audio_file, name=f"{filename}.mp3")
                        media.downloaded_at = timezone.now()
                        media.save()
                    print(f"✅ Downloaded and saved audio for: {url}")
                else:
                    print(f"❌ Audio file not found at {absolute_audio_path}")

            except Exception as e:
                print(f"❌ Error downloading audio for {url}: {e}")
    else:
        print("No new media URLs to download.")