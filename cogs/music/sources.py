import re
import urllib.request
import logging

logger = logging.getLogger("SosaBot.Music.Sources")

YTDL_SEARCH_OPTIONS = {
    'format': 'bestaudio/best',
    'extract_flat': 'in_playlist',
    'default_search': 'ytsearch',
    'quiet': True,
    'no_warnings': True,
    'ignoreerrors': True
}

YTDL_STREAM_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'no_warnings': True,
    'ignoreerrors': True
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def get_clean_url(entry: dict) -> str | None:
    """Trích xuất URL sạch từ entry của yt-dlp"""
    url = entry.get('webpage_url') or entry.get('url')
    if url and url.startswith('http'):
        return url
    if entry.get('id'):
        return f"https://www.youtube.com/watch?v={entry.get('id')}"
    return None

def get_title(entry: dict) -> str:
    """Lọc tên bài hát thông minh cho cả YouTube và SoundCloud"""
    title = entry.get('title') or entry.get('track') or entry.get('alt_title')
    if not title:
        url = entry.get('url') or entry.get('webpage_url') or ''
        if url and '/' in url:
            title = url.split('/')[-1].replace('-', ' ').title()
        else:
            title = 'Unknown'
    return title

def resolve_spotify_link(url: str) -> str | None:
    """Trích xuất tiêu đề bài hát từ link Spotify để tìm kiếm trên YouTube"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
        title_match = re.search(r'<title>(.+?)</title>', html)
        if title_match:
            title = title_match.group(1)
            clean_title = title.replace(" | Spotify", "").replace(" - song and lyrics by ", " ")
            return clean_title
    except Exception as e:
        logger.warning(f"Lỗi đọc metadata Spotify: {e}")
    return None
