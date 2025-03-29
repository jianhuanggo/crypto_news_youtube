"""
Module for downloading YouTube videos.
"""

import os
import logging
from typing import Dict, Any, Optional
from pytube import YouTube
from pytube.exceptions import PytubeError

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoDownloader:
    """Class for downloading YouTube videos."""

    def __init__(self, download_dir: str = None):
        """
        Initialize the video downloader.

        Args:
            download_dir: Directory to save downloaded videos. If None, uses the directory from config.
        """
        self.download_dir = download_dir or config.DOWNLOAD_DIR

        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            logger.info(f"Created download directory: {self.download_dir}")

    def download_video(self, video_info: Dict[str, Any]) -> Optional[str]:
        """
        Download a YouTube video.

        Args:
            video_info: Dictionary containing video information

        Returns:
            Path to the downloaded video file or None if download failed
        """
        video_id = video_info['id']
        video_url = video_info['url']
        channel_title = video_info['channel_title']

        channel_dir = os.path.join(
            self.download_dir,
            self._sanitize_filename(channel_title))
        if not os.path.exists(channel_dir):
            os.makedirs(channel_dir)

        try:
            yt = YouTube(video_url)

            stream = yt.streams.filter(
                progressive=True,
                file_extension='mp4').order_by('resolution').desc().first()

            if not stream:
                logger.warning(
                    f"No suitable stream found for video: {video_id}")
                return None

            logger.info(
                f"Downloading video: {
                    video_info['title']} ({video_id})")
            video_path = stream.download(output_path=channel_dir)

            logger.info(f"Successfully downloaded video to: {video_path}")
            return video_path

        except PytubeError as e:
            logger.error(f"Error downloading video {video_id}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error downloading video {video_id}: {e}")
            return None

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename by removing invalid characters.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        if len(filename) > 100:
            filename = filename[:100]

        return filename
