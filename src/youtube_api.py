"""
Module for interacting with the YouTube API.
"""

import logging
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YouTubeAPI:
    """Class for interacting with the YouTube Data API."""

    def __init__(self, api_key: str = None):
        """
        Initialize the YouTube API client.

        Args:
            api_key: YouTube Data API key. If None, uses the key from config.
        """
        self.api_key = api_key or config.YOUTUBE_API_KEY
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        logger.info("YouTube API client initialized")

    def search_channels(
            self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for YouTube channels based on a query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of channel information dictionaries
        """
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='snippet',
                maxResults=max_results,
                type='channel'
            ).execute()

            channels = []
            for item in search_response.get('items', []):
                channel_id = item['snippet']['channelId']
                channel_info = self.get_channel_info(channel_id)
                if channel_info:
                    channels.append(channel_info)

            logger.info(f"Found {len(channels)} channels for query: {query}")
            return channels

        except HttpError as e:
            logger.error(f"Error searching for channels: {e}")
            return []

    def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a YouTube channel.

        Args:
            channel_id: YouTube channel ID

        Returns:
            Dictionary containing channel information or None if error
        """
        try:
            channel_response = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                id=channel_id
            ).execute()

            if not channel_response.get('items'):
                logger.warning(f"No channel found with ID: {channel_id}")
                return None

            item = channel_response['items'][0]
            channel_info = {
                'id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'subscriber_count': item['statistics'].get('subscriberCount', 'N/A'),
                'video_count': item['statistics'].get('videoCount', 'N/A'),
                'view_count': item['statistics'].get('viewCount', 'N/A'),
                'uploads_playlist': item['contentDetails']['relatedPlaylists']['uploads']
            }

            return channel_info

        except HttpError as e:
            logger.error(f"Error getting channel info for {channel_id}: {e}")
            return None

    def get_channel_videos(self, channel_id: str,
                           max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent videos from a YouTube channel.

        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to return

        Returns:
            List of video information dictionaries
        """
        try:
            channel_info = self.get_channel_info(channel_id)
            if not channel_info:
                return []

            uploads_playlist_id = channel_info['uploads_playlist']

            playlist_response = self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()

            videos = []
            for item in playlist_response.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_info = self.get_video_info(video_id)
                if video_info:
                    videos.append(video_info)

            logger.info(
                f"Retrieved {
                    len(videos)} videos for channel: {channel_id}")
            return videos

        except HttpError as e:
            logger.error(f"Error getting videos for channel {channel_id}: {e}")
            return []

    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary containing video information or None if error
        """
        try:
            video_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()

            if not video_response.get('items'):
                logger.warning(f"No video found with ID: {video_id}")
                return None

            item = video_response['items'][0]

            duration_iso = item['contentDetails']['duration']
            duration_seconds = self._parse_duration(duration_iso)

            if (duration_seconds < config.MIN_VIDEO_LENGTH_SECONDS or
                    duration_seconds > config.MAX_VIDEO_LENGTH_SECONDS):
                logger.info(
                    f"Video {video_id} duration ({duration_seconds}s) outside acceptable range")
                return None

            video_info = {
                'id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'channel_id': item['snippet']['channelId'],
                'channel_title': item['snippet']['channelTitle'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'duration': duration_iso,
                'duration_seconds': duration_seconds,
                'view_count': item['statistics'].get('viewCount', 'N/A'),
                'like_count': item['statistics'].get('likeCount', 'N/A'),
                'comment_count': item['statistics'].get('commentCount', 'N/A'),
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }

            return video_info

        except HttpError as e:
            logger.error(f"Error getting video info for {video_id}: {e}")
            return None

    def _parse_duration(self, duration_iso: str) -> int:
        """
        Parse ISO 8601 duration format to seconds.

        Args:
            duration_iso: Duration in ISO 8601 format (e.g., 'PT1H2M3S')

        Returns:
            Duration in seconds
        """
        duration_seconds = 0

        duration = duration_iso[2:]

        hours = 0
        minutes = 0
        seconds = 0

        if 'H' in duration:
            hours_split = duration.split('H')
            hours = int(hours_split[0])
            duration = hours_split[1]

        if 'M' in duration:
            minutes_split = duration.split('M')
            minutes = int(minutes_split[0])
            duration = minutes_split[1]

        if 'S' in duration:
            seconds = int(duration.split('S')[0])

        duration_seconds = hours * 3600 + minutes * 60 + seconds
        return duration_seconds
