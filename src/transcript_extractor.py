"""
Module for extracting transcripts from YouTube videos.
"""

import os
import logging
from typing import Dict, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    CouldNotRetrieveTranscript
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TranscriptExtractor:
    """Class for extracting transcripts from YouTube videos."""

    def __init__(self):
        """Initialize the transcript extractor."""
        self.formatter = TextFormatter()
        logger.info("Transcript extractor initialized")

    def extract_transcript(self, video_info: Dict[str, Any]) -> Optional[str]:
        """
        Extract transcript from a YouTube video.

        Args:
            video_info: Dictionary containing video information

        Returns:
            Transcript text or None if extraction failed
        """
        video_id = video_info['id']

        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

            transcript_text = self.formatter.format_transcript(transcript_list)

            logger.info(
                f"Successfully extracted transcript for video: {video_id}")
            return transcript_text

        except TranscriptsDisabled:
            logger.warning(f"Transcripts are disabled for video: {video_id}")
            return None

        except NoTranscriptFound:
            logger.warning(f"No transcript found for video: {video_id}")
            return None

        except CouldNotRetrieveTranscript as e:
            logger.error(
                f"Could not retrieve transcript for video {video_id}: {e}")
            return None

        except Exception as e:
            logger.error(
                f"Unexpected error extracting transcript for video {video_id}: {e}")
            return None

    def save_transcript(self,
                        video_info: Dict[str,
                                         Any],
                        transcript: str,
                        output_dir: str) -> Optional[str]:
        """
        Save transcript to a file.

        Args:
            video_info: Dictionary containing video information
            transcript: Transcript text
            output_dir: Directory to save the transcript

        Returns:
            Path to the saved transcript file or None if saving failed
        """
        if not transcript:
            return None

        video_id = video_info['id']
        video_title = video_info['title']
        channel_title = video_info['channel_title']

        channel_dir = os.path.join(
            output_dir, self._sanitize_filename(channel_title))
        if not os.path.exists(channel_dir):
            os.makedirs(channel_dir)

        transcript_filename = f"{
            self._sanitize_filename(video_title)}_{video_id}_transcript.txt"
        transcript_path = os.path.join(channel_dir, transcript_filename)

        try:
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(transcript)

            logger.info(f"Saved transcript to: {transcript_path}")
            return transcript_path

        except Exception as e:
            logger.error(f"Error saving transcript for video {video_id}: {e}")
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
