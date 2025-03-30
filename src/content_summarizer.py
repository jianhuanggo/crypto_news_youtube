"""
Module for summarizing video content using NLP.
"""

import os
import logging
from typing import Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentSummarizer:
    """Class for summarizing video content using NLP."""

    def __init__(self, model_name: str = None):
        """
        Initialize the content summarizer.

        Args:
            model_name: Name of the HuggingFace model to use. If None, uses the model from config.
        """
        self.model_name = model_name or config.SUMMARIZATION_MODEL

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        logger.info(f"Loading summarization model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name).to(self.device)
        logger.info("Summarization model loaded")

    def summarize(
            self,
            text: str,
            min_length: int = None,
            max_length: int = None) -> str:
        """
        Generate a summary of the input text.

        Args:
            text: Input text to summarize
            min_length: Minimum length of the summary in words. If None, uses the value from config.
            max_length: Maximum length of the summary in words. If None, uses the value from config.

        Returns:
            Generated summary
        """
        min_length = min_length or config.SUMMARY_MIN_LENGTH
        max_length = max_length or config.SUMMARY_MAX_LENGTH

        if not text or len(text.split()) < min_length:
            logger.warning("Text is too short to summarize")
            return text

        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=1024,
                truncation=True).to(
                self.device)

            summary_ids = self.model.generate(
                inputs["input_ids"],
                num_beams=4,
                min_length=min_length,
                max_length=max_length,
                early_stopping=True
            )

            summary = self.tokenizer.decode(
                summary_ids[0], skip_special_tokens=True)

            logger.info(
                f"Generated summary of length: {len(summary.split())} words")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Error generating summary."

    def summarize_transcript(
            self, video_info: Dict[str, Any], transcript: str) -> Optional[Dict[str, Any]]:
        """
        Summarize a video transcript.

        Args:
            video_info: Dictionary containing video information
            transcript: Video transcript text

        Returns:
            Dictionary containing the video information and summary
        """
        if not transcript:
            logger.warning(
                f"No transcript provided for video: {
                    video_info['id']}")
            return None

        try:
            summary = self.summarize(transcript)

            summary_info = {
                **video_info,
                'transcript': transcript,
                'summary': summary
            }

            logger.info(
                f"Successfully summarized transcript for video: {
                    video_info['id']}")
            return summary_info

        except Exception as e:
            logger.error(
                f"Error summarizing transcript for video {
                    video_info['id']}: {e}")
            return None

    def save_summary(self,
                     summary_info: Dict[str,
                                        Any],
                     output_dir: str) -> Optional[str]:
        """
        Save summary to a file.

        Args:
            summary_info: Dictionary containing video information and summary
            output_dir: Directory to save the summary

        Returns:
            Path to the saved summary file or None if saving failed
        """
        if not summary_info or 'summary' not in summary_info:
            return None

        video_id = summary_info['id']
        video_title = summary_info['title']
        channel_title = summary_info['channel_title']

        channel_dir = os.path.join(
            output_dir, self._sanitize_filename(channel_title))
        if not os.path.exists(channel_dir):
            os.makedirs(channel_dir)

        summary_filename = f"{
            self._sanitize_filename(video_title)}_{video_id}_summary.txt"
        summary_path = os.path.join(channel_dir, summary_filename)

        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"Title: {video_title}\n")
                f.write(f"Channel: {channel_title}\n")
                f.write(f"URL: {summary_info['url']}\n")
                f.write(f"Published: {summary_info['published_at']}\n")
                f.write(f"Duration: {summary_info['duration']}\n")
                f.write(f"Views: {summary_info['view_count']}\n\n")
                f.write("Summary:\n")
                f.write(summary_info['summary'])

            logger.info(f"Saved summary to: {summary_path}")
            return summary_path

        except Exception as e:
            logger.error(f"Error saving summary for video {video_id}: {e}")
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
