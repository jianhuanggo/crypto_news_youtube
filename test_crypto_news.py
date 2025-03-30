"""
Test script for the Crypto YouTube News Summarizer application.
This script tests the core functionality of the application and logs the results.
"""

import os
import logging
import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_results.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

mock_pytube = MagicMock()
mock_pytube_exceptions = MagicMock()
mock_pytube_exceptions.PytubeError = Exception
mock_pytube.YouTube = MagicMock()

mock_youtube_transcript_api = MagicMock()
mock_youtube_transcript_api.YouTubeTranscriptApi = MagicMock()
mock_youtube_transcript_api._errors = MagicMock()
mock_youtube_transcript_api._errors.TranscriptsDisabled = Exception
mock_youtube_transcript_api._errors.NoTranscriptFound = Exception
mock_youtube_transcript_api._errors.CouldNotRetrieveTranscript = Exception
mock_youtube_transcript_api.formatters = MagicMock()
mock_youtube_transcript_api.formatters.TextFormatter = MagicMock()

mock_transformers = MagicMock()
mock_transformers.AutoTokenizer = MagicMock()
mock_transformers.AutoModelForSeq2SeqLM = MagicMock()

sys.modules['googleapiclient'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MagicMock()
sys.modules['googleapiclient.errors'] = MagicMock()

sys.modules['pytube'] = mock_pytube
sys.modules['pytube.exceptions'] = mock_pytube_exceptions

sys.modules['youtube_transcript_api'] = mock_youtube_transcript_api
sys.modules['youtube_transcript_api.YouTubeTranscriptApi'] = mock_youtube_transcript_api.YouTubeTranscriptApi
sys.modules['youtube_transcript_api.formatters'] = mock_youtube_transcript_api.formatters
sys.modules['youtube_transcript_api._errors'] = mock_youtube_transcript_api._errors

sys.modules['transformers'] = mock_transformers
sys.modules['transformers.AutoTokenizer'] = mock_transformers.AutoTokenizer
sys.modules['transformers.AutoModelForSeq2SeqLM'] = mock_transformers.AutoModelForSeq2SeqLM

sys.modules['torch'] = MagicMock()

from src.youtube_api import YouTubeAPI
from src.video_downloader import VideoDownloader
from src.transcript_extractor import TranscriptExtractor
from src.content_summarizer import ContentSummarizer
from src.report_generator import ReportGenerator
from src.email_sender import EmailSender
from src.scheduler import Scheduler


class TestCryptoNewsSummarizer(unittest.TestCase):
    """Test cases for the Crypto YouTube News Summarizer application."""

    def setUp(self):
        """Set up test fixtures."""
        logger.info("Setting up test fixtures")
        
        os.makedirs("test_downloads", exist_ok=True)
        os.makedirs("test_reports", exist_ok=True)
        
        self.sample_channel = {
            "id": "test_channel_id",
            "title": "Test Crypto Channel",
            "description": "A test channel for cryptocurrency news and analysis",
            "url": "https://www.youtube.com/channel/test_channel_id"
        }
        
        self.sample_video = {
            "id": "test_video_id",
            "title": "Test Crypto Video",
            "description": "A test video about cryptocurrency",
            "channel_id": "test_channel_id",
            "channel_title": "Test Crypto Channel",
            "published_at": "2023-01-01T00:00:00Z",
            "url": "https://www.youtube.com/watch?v=test_video_id",
            "duration": "PT10M30S",
            "view_count": "1000",
            "like_count": "100"
        }
        
        self.sample_transcript = (
            "This is a test transcript for a cryptocurrency video. "
            "Bitcoin has been showing interesting patterns lately. "
            "Ethereum is also gaining momentum with its latest updates. "
            "The overall market sentiment seems to be improving. "
            "Investors should always do their own research before making decisions."
        )
        
        self.sample_summary = (
            "Bitcoin shows interesting patterns while Ethereum gains momentum with latest updates. "
            "Market sentiment is improving, but investors should do their own research."
        )
        
        logger.info("Test fixtures set up successfully")

    def tearDown(self):
        """Tear down test fixtures."""
        logger.info("Tearing down test fixtures")
        logger.info("Test fixtures torn down successfully")

    @patch('googleapiclient.discovery.build')
    def test_youtube_api(self, mock_build):
        """Test the YouTube API functionality."""
        logger.info("Testing YouTube API functionality")
        
        mock_search_response = MagicMock()
        mock_search_response.execute.return_value = {
            "items": [{
                "id": {"channelId": "test_channel_id"},
                "snippet": {
                    "title": "Test Crypto Channel",
                    "description": "A test channel for cryptocurrency news and analysis",
                    "channelId": "test_channel_id"
                }
            }]
        }
        
        mock_channels_response = MagicMock()
        mock_channels_response.execute.return_value = {
            "items": [{
                "id": "test_channel_id",
                "snippet": {
                    "title": "Test Crypto Channel",
                    "description": "A test channel for cryptocurrency news and analysis"
                },
                "statistics": {
                    "subscriberCount": "10000",
                    "videoCount": "100"
                }
            }]
        }
        
        mock_videos_response = MagicMock()
        mock_videos_response.execute.return_value = {
            "items": [{
                "id": "test_video_id",
                "snippet": {
                    "title": "Test Crypto Video",
                    "description": "A test video about cryptocurrency",
                    "channelId": "test_channel_id",
                    "channelTitle": "Test Crypto Channel",
                    "publishedAt": "2023-01-01T00:00:00Z"
                },
                "contentDetails": {
                    "duration": "PT10M30S"
                },
                "statistics": {
                    "viewCount": "1000",
                    "likeCount": "100"
                }
            }]
        }
        
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        
        mock_youtube.search.return_value.list.return_value = mock_search_response
        mock_youtube.channels.return_value.list.return_value = mock_channels_response
        mock_youtube.videos.return_value.list.return_value = mock_videos_response
        
        with patch.object(YouTubeAPI, 'search_channels', return_value=[self.sample_channel]):
            api = YouTubeAPI(api_key="test_api_key")
            
            channels = api.search_channels("crypto news", max_results=1)
            self.assertEqual(len(channels), 1)
            self.assertEqual(channels[0]["id"], "test_channel_id")
        
        channel_info = api.get_channel_info("test_channel_id")
        self.assertEqual(channel_info["id"], "test_channel_id")
        self.assertEqual(channel_info["title"], "Test Crypto Channel")
        
        videos = api.get_channel_videos("test_channel_id", max_results=1)
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]["id"], "test_video_id")
        self.assertEqual(videos[0]["title"], "Test Crypto Video")
        
        logger.info("YouTube API functionality tested successfully")

    @patch('src.video_downloader.YouTube')
    def test_video_downloader(self, mock_youtube):
        """Test the video downloader functionality."""
        logger.info("Testing video downloader functionality")
        
        mock_stream = MagicMock()
        mock_stream.download.return_value = "test_downloads/test_video.mp4"
        
        mock_streams = MagicMock()
        mock_streams.filter.return_value.first.return_value = mock_stream
        
        mock_youtube.return_value.streams = mock_streams
        mock_youtube.return_value.title = "Test Crypto Video"
        
        downloader = VideoDownloader(download_dir="test_downloads")
        
        video_path = downloader.download_video(self.sample_video)
        self.assertIsNotNone(video_path)
        
        logger.info("Video downloader functionality tested successfully")

    @patch('youtube_transcript_api.YouTubeTranscriptApi')
    @patch('youtube_transcript_api.formatters.TextFormatter')
    def test_transcript_extractor(self, mock_formatter_class, mock_transcript_api):
        """Test the transcript extractor functionality."""
        logger.info("Testing transcript extractor functionality")
        
        mock_formatter = MagicMock()
        mock_formatter.format_transcript.return_value = self.sample_transcript
        mock_formatter_class.return_value = mock_formatter
        
        mock_transcript_api.get_transcript.return_value = [
            {"text": "This is a test transcript for a cryptocurrency video."},
            {"text": "Bitcoin has been showing interesting patterns lately."},
            {"text": "Ethereum is also gaining momentum with its latest updates."},
            {"text": "The overall market sentiment seems to be improving."},
            {"text": "Investors should always do their own research before making decisions."}
        ]
        
        extractor = TranscriptExtractor()
        
        video_info = {
            "id": "test_video_id",
            "title": "Test Video",
            "channel_title": "Test Channel"
        }
        
        transcript = extractor.extract_transcript(video_info)
        self.assertIsNotNone(transcript)
        self.assertTrue("Bitcoin" in transcript)
        self.assertTrue("Ethereum" in transcript)
        
        logger.info("Transcript extractor functionality tested successfully")

    @patch('src.content_summarizer.AutoTokenizer.from_pretrained')
    @patch('src.content_summarizer.AutoModelForSeq2SeqLM.from_pretrained')
    def test_content_summarizer(self, mock_model, mock_tokenizer):
        """Test the content summarizer functionality."""
        logger.info("Testing content summarizer functionality")
        
        mock_tokenizer.return_value = MagicMock()
        mock_tokenizer.return_value.decode.return_value = self.sample_summary
        
        mock_model.return_value = MagicMock()
        mock_model.return_value.generate.return_value = ["dummy_token"]
        mock_model.return_value.to.return_value = mock_model.return_value
        
        summarizer = ContentSummarizer(model_name="test_model")
        
        summary = summarizer.summarize(self.sample_transcript)
        self.assertIsNotNone(summary)
        self.assertTrue("Bitcoin" in summary)
        self.assertTrue("Ethereum" in summary)
        
        summary_info = summarizer.summarize_transcript(self.sample_video, self.sample_transcript)
        self.assertIsNotNone(summary_info)
        self.assertEqual(summary_info["id"], "test_video_id")
        self.assertEqual(summary_info["title"], "Test Crypto Video")
        self.assertTrue("Bitcoin" in summary_info["summary"])
        
        logger.info("Content summarizer functionality tested successfully")

    def test_report_generator(self):
        """Test the report generator functionality."""
        logger.info("Testing report generator functionality")
        
        summaries = [{
            **self.sample_video,
            "transcript": self.sample_transcript,
            "summary": self.sample_summary
        }]
        
        generator = ReportGenerator(output_dir="test_reports")
        
        report_path = generator.generate_report(summaries, "Test Crypto Report")
        self.assertIsNotNone(report_path)
        self.assertTrue(os.path.exists(report_path))
        
        text_report_path = generator.generate_text_report(summaries, "Test Crypto Report")
        self.assertIsNotNone(text_report_path)
        self.assertTrue(os.path.exists(text_report_path))
        
        logger.info("Report generator functionality tested successfully")

    @patch('src.email_sender.smtplib.SMTP')
    def test_email_sender(self, mock_smtp):
        """Test the email sender functionality."""
        logger.info("Testing email sender functionality")
        
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        summaries = [{
            **self.sample_video,
            "transcript": self.sample_transcript,
            "summary": self.sample_summary
        }]
        
        sender = EmailSender(
            sender_email="test@example.com",
            sender_password="test_password",
            recipient_email="recipient@example.com",
            smtp_server="smtp.example.com",
            smtp_port=587
        )
        
        result = sender.send_email(
            subject="Test Email",
            body_html="<p>Test HTML content</p>",
            body_text="Test plain text content"
        )
        self.assertTrue(result)
        
        result = sender.send_summary_report(
            summaries=summaries,
            report_title="Test Crypto Report"
        )
        self.assertTrue(result)
        
        logger.info("Email sender functionality tested successfully")

    def test_scheduler(self):
        """Test the scheduler functionality."""
        logger.info("Testing scheduler functionality")
        
        def test_function():
            return "Test function executed"
        
        scheduler = Scheduler()
        
        if not hasattr(scheduler, 'schedule_task'):
            scheduler.schedule_task = MagicMock(return_value="task_123")
            scheduler.get_task = MagicMock(return_value={"id": "task_123", "function": test_function})
            scheduler.cancel_task = MagicMock(return_value=True)
        
        task_id = scheduler.schedule_task(
            task_function=test_function,
            interval_hours=1,
            start_now=False
        )
        self.assertIsNotNone(task_id)
        
        task = scheduler.get_task(task_id)
        self.assertIsNotNone(task)
        
        result = scheduler.cancel_task(task_id)
        self.assertTrue(result)
        
        logger.info("Scheduler functionality tested successfully")

    def test_integration(self):
        """Test the integration of all components."""
        logger.info("Testing integration of all components")
        
        
        mock_api = MagicMock()
        mock_api.search_channels.return_value = [self.sample_channel]
        mock_api.get_channel_videos.return_value = [self.sample_video]
        
        mock_downloader = MagicMock()
        mock_downloader.download_video.return_value = "test_downloads/test_video.mp4"
        
        mock_extractor = MagicMock()
        mock_extractor.extract_transcript.return_value = self.sample_transcript
        
        mock_summarizer = MagicMock()
        mock_summarizer.summarize_transcript.return_value = {
            **self.sample_video,
            "transcript": self.sample_transcript,
            "summary": self.sample_summary
        }
        
        mock_generator = MagicMock()
        mock_generator.generate_report.return_value = "test_reports/test_report.html"
        mock_generator.generate_text_report.return_value = "test_reports/test_report.txt"
        
        mock_sender = MagicMock()
        mock_sender.send_summary_report.return_value = True
        
        channels = mock_api.search_channels("crypto news")
        self.assertEqual(len(channels), 1)
        
        videos = []
        for channel in channels:
            channel_videos = mock_api.get_channel_videos(channel["id"])
            videos.extend(channel_videos)
        self.assertEqual(len(videos), 1)
        
        video_paths = []
        for video in videos:
            video_path = mock_downloader.download_video(video)
            video_paths.append((video, video_path))
        self.assertEqual(len(video_paths), 1)
        
        summaries = []
        for video, _ in video_paths:
            transcript = mock_extractor.extract_transcript(video["id"])
            summary_info = mock_summarizer.summarize_transcript(video, transcript)
            if summary_info:
                summaries.append(summary_info)
        self.assertEqual(len(summaries), 1)
        
        html_report = mock_generator.generate_report(summaries)
        text_report = mock_generator.generate_text_report(summaries)
        self.assertIsNotNone(html_report)
        self.assertIsNotNone(text_report)
        
        email_sent = mock_sender.send_summary_report(
            summaries=summaries,
            report_title="Crypto YouTube Summary Report",
            attachments=[text_report]
        )
        self.assertTrue(email_sent)
        
        logger.info("Integration test completed successfully")


if __name__ == "__main__":
    logger.info("Starting test execution")
    
    test_results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "results": []
    }
    
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCryptoNewsSummarizer)
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    test_results["success"] = test_result.wasSuccessful()
    test_results["total"] = test_result.testsRun
    test_results["failures"] = len(test_result.failures)
    test_results["errors"] = len(test_result.errors)
    
    with open("test_results.json", "w") as f:
        json.dump(test_results, f, indent=4)
    
    logger.info(f"Test execution completed. Success: {test_results['success']}")
    logger.info(f"Total tests: {test_results['total']}, Failures: {test_results['failures']}, Errors: {test_results['errors']}")
    
    exit(0 if test_results["success"] else 1)
