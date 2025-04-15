import os
import re
import subprocess
import xml.etree.ElementTree as ET

import requests
from background_task import background
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files import File
from django.utils import timezone

from .models import DownloadedAudio, MediaURL, YouTubeChannel


def get_channel_id(youtube_url):
    """Extract channelId from YouTube channel page source."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(youtube_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        meta = soup.find("meta", property="og:url")
        if meta and "/channel/" in meta.get("content", ""):
            return meta["content"].split("/channel/")[1].split("?")[0]

        link = soup.find("link", rel="canonical")
        if link and "/channel/" in link.get("href", ""):
            return link["href"].split("/channel/")[1].split("?")[0]

    except Exception as e:
        print("❌ Error extracting channel ID:", e)
    return None


def fetch_and_save_media_urls(youtube_channel):
    """Fetch media URLs and store in MediaURL model."""
    if not youtube_channel.channel_id:
        channel_id = get_channel_id(youtube_channel.url)
        if channel_id:
            youtube_channel.channel_id = channel_id
            youtube_channel.save()
        else:
            return

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
                if url and not MediaURL.objects.filter(media_url=url).exists():
                    MediaURL.objects.create(
                        youtube_channel=youtube_channel,
                        media_url=url,
                        created_at=timezone.now(),
                    )
                    print(f"✅ New media URL saved: {url}")
    except Exception as e:
        print("❌ Error fetching RSS:", e)


@background(schedule=1)  # Run every 60 seconds
def check_and_update_media_urls():
    """Background task to check and update media URLs for all YouTube channels."""
    youtube_channels = YouTubeChannel.objects.all()

    for youtube_channel in youtube_channels:
        print(
            f"Checking updates for YouTube Channel: {youtube_channel.name} ({youtube_channel.channel_id})"
        )

        if not youtube_channel.channel_id:
            channel_id = get_channel_id(youtube_channel.url)
            if channel_id:
                youtube_channel.channel_id = channel_id
                youtube_channel.save()
            else:
                print(f"❌ Could not determine channel ID for {youtube_channel.name}")
                continue

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
                MediaURL.objects.filter(youtube_channel=youtube_channel).values_list(
                    "media_url", flat=True
                )
            )

            for entry in root.findall("atom:entry", ns):
                media_content = entry.find("media:group/media:content", ns)
                if media_content is not None:
                    url = media_content.attrib.get("url")
                    if url and url not in existing_urls:
                        MediaURL.objects.create(
                            youtube_channel=youtube_channel,
                            media_url=url,
                            created_at=timezone.now(),
                        )
                        print(f"✅ New media URL added: {url}")
                        existing_urls.add(url)
                    else:
                        print(f"Media URL already exists: {url}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching RSS for {youtube_channel.name}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


@background(schedule=3)  # Run every 5 minutes
def download_audio():
    """Background task to download audio from YouTube URLs."""
    audio_dir = os.path.join(settings.MEDIA_ROOT, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    media_urls = MediaURL.objects.exclude(
        id__in=DownloadedAudio.objects.values("media_url")
    )

    if media_urls.exists():
        for media in media_urls:
            url = media.media_url

            try:
                filename = url.split("/")[-1]
                filename = re.sub(r"\?.*$", "", filename)
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

                if not os.path.exists(absolute_audio_path):
                    raise FileNotFoundError(
                        f"Audio file not found at {absolute_audio_path}"
                    )

                with open(absolute_audio_path, "rb") as audio_file:
                    downloaded_audio = DownloadedAudio(
                        media_url=media,
                        audio_file=File(audio_file, name=f"{filename}.mp3"),
                    )
                    downloaded_audio.save()

                print(f"✅ Downloaded and saved audio for: {url}")

            except subprocess.CalledProcessError as e:
                print(f"yt-dlp failed for {url}: {e}")
            except FileNotFoundError as e:
                print(f"File error for {url}: {e}")
            except Exception as e:
                print(f"Unexpected error for {url}: {str(e)}")
    else:
        print("No new media URLs to download.")
