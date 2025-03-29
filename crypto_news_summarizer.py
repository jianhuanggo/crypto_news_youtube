"""
Crypto YouTube News Summarizer

This script automates the process of finding cryptocurrency-focused YouTube channels,
downloading their recent videos, summarizing the content, and emailing comprehensive reports.
"""

import config
from src.scheduler import Scheduler
from src.email_sender import EmailSender
from src.report_generator import ReportGenerator
from src.content_summarizer import ContentSummarizer
from src.transcript_extractor import TranscriptExtractor
from src.video_downloader import VideoDownloader
from src.youtube_api import YouTubeAPI
import os
import sys
import logging
import argparse
import time
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crypto_news_summarizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Crypto YouTube News Summarizer")

    parser.add_argument(
        "--search-queries",
        nargs="+",
        help="Search queries for finding crypto YouTube channels"
    )

    parser.add_argument(
        "--max-channels",
        type=int,
        default=config.MAX_SEARCH_RESULTS,
        help="Maximum number of channels to process"
    )

    parser.add_argument(
        "--videos-per-channel",
        type=int,
        default=config.VIDEOS_PER_CHANNEL,
        help="Number of recent videos to download per channel"
    )

    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip video download step (use existing downloads)"
    )

    parser.add_argument(
        "--skip-email",
        action="store_true",
        help="Skip sending email report"
    )

    parser.add_argument(
        "--email-recipient",
        help="Email address to send the report to (overrides config)"
    )

    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run the script on a schedule"
    )

    parser.add_argument(
        "--schedule-interval",
        type=int,
        default=config.SCHEDULE_INTERVAL,
        help="Interval in hours between scheduled runs"
    )

    return parser.parse_args()


def find_crypto_channels(youtube_api: YouTubeAPI,
                         search_queries: List[str],
                         max_channels: int) -> List[Dict[str,
                                                         Any]]:
    """
    Find cryptocurrency-focused YouTube channels.

    Args:
        youtube_api: YouTubeAPI instance
        search_queries: List of search queries
        max_channels: Maximum number of channels to return

    Returns:
        List of channel information dictionaries
    """
    logger.info(
        f"Searching for crypto YouTube channels using {
            len(search_queries)} queries")

    all_channels = []
    channels_by_id = {}

    for query in search_queries:
        logger.info(f"Searching for channels with query: {query}")
        channels = youtube_api.search_channels(query, max_results=max_channels)

        for channel in channels:
            channel_id = channel['id']

            if channel_id in channels_by_id:
                continue

            is_relevant = is_crypto_relevant(channel)

            if is_relevant:
                channels_by_id[channel_id] = channel
                all_channels.append(channel)
                logger.info(
                    f"Found relevant crypto channel: {
                        channel['title']} (ID: {channel_id})")

    logger.info(f"Found {len(all_channels)} relevant crypto channels")

    return all_channels[:max_channels]


def is_crypto_relevant(channel: Dict[str, Any]) -> bool:
    """
    Determine if a channel is relevant to cryptocurrency.

    Args:
        channel: Channel information dictionary

    Returns:
        True if the channel is relevant to cryptocurrency, False otherwise
    """
    crypto_keywords = [
        'crypto', 'cryptocurrency', 'bitcoin', 'btc', 'ethereum', 'eth',
        'blockchain', 'defi', 'nft', 'altcoin', 'trading', 'binance',
        'coinbase', 'token', 'mining', 'wallet', 'ledger', 'trezor'
    ]

    title = channel['title'].lower()
    description = channel['description'].lower()

    keyword_matches = 0
    for keyword in crypto_keywords:
        if keyword in title or keyword in description:
            keyword_matches += 1

    relevance_score = keyword_matches / len(crypto_keywords)

    return relevance_score >= config.CHANNEL_RELEVANCE_THRESHOLD


def download_channel_videos(
    youtube_api: YouTubeAPI,
    video_downloader: VideoDownloader,
    channel: Dict[str, Any],
    videos_per_channel: int
) -> List[Dict[str, Any]]:
    """
    Download recent videos from a YouTube channel.

    Args:
        youtube_api: YouTubeAPI instance
        video_downloader: VideoDownloader instance
        channel: Channel information dictionary
        videos_per_channel: Number of recent videos to download

    Returns:
        List of video information dictionaries with download paths
    """
    channel_id = channel['id']
    channel_title = channel['title']

    logger.info(
        f"Getting recent videos for channel: {channel_title} (ID: {channel_id})")

    videos = youtube_api.get_channel_videos(
        channel_id, max_results=videos_per_channel)

    if not videos:
        logger.warning(f"No videos found for channel: {channel_title}")
        return []

    logger.info(f"Found {len(videos)} videos for channel: {channel_title}")

    downloaded_videos = []
    for video in videos:
        video_id = video['id']
        video_title = video['title']

        logger.info(f"Downloading video: {video_title} (ID: {video_id})")

        video_path = video_downloader.download_video(video)

        if video_path:
            video['download_path'] = video_path
            downloaded_videos.append(video)
            logger.info(f"Successfully downloaded video: {video_title}")
        else:
            logger.warning(f"Failed to download video: {video_title}")

    logger.info(
        f"Downloaded {
            len(downloaded_videos)} videos for channel: {channel_title}")
    return downloaded_videos


def process_videos(
    transcript_extractor: TranscriptExtractor,
    content_summarizer: ContentSummarizer,
    videos: List[Dict[str, Any]],
    transcript_dir: str = "transcripts",
    summary_dir: str = "summaries"
) -> List[Dict[str, Any]]:
    """
    Process videos by extracting transcripts and generating summaries.

    Args:
        transcript_extractor: TranscriptExtractor instance
        content_summarizer: ContentSummarizer instance
        videos: List of video information dictionaries
        transcript_dir: Directory to save transcripts
        summary_dir: Directory to save summaries

    Returns:
        List of video information dictionaries with transcripts and summaries
    """
    logger.info(f"Processing {len(videos)} videos")

    os.makedirs(transcript_dir, exist_ok=True)
    os.makedirs(summary_dir, exist_ok=True)

    processed_videos = []
    for video in videos:
        video_id = video['id']
        video_title = video['title']

        logger.info(f"Processing video: {video_title} (ID: {video_id})")

        transcript = transcript_extractor.extract_transcript(video)

        if transcript:
            transcript_path = transcript_extractor.save_transcript(
                video, transcript, transcript_dir)

            if transcript_path:
                video['transcript_path'] = transcript_path

                summary_info = content_summarizer.summarize_transcript(
                    video, transcript)

                if summary_info:
                    summary_path = content_summarizer.save_summary(
                        summary_info, summary_dir)

                    if summary_path:
                        summary_info['summary_path'] = summary_path
                        processed_videos.append(summary_info)
                        logger.info(
                            f"Successfully processed video: {video_title}")
                    else:
                        logger.warning(
                            f"Failed to save summary for video: {video_title}")
                else:
                    logger.warning(
                        f"Failed to generate summary for video: {video_title}")
            else:
                logger.warning(
                    f"Failed to save transcript for video: {video_title}")
        else:
            logger.warning(
                f"Failed to extract transcript for video: {video_title}")

    logger.info(f"Successfully processed {len(processed_videos)} videos")
    return processed_videos


def run_workflow(args):
    """
    Run the Crypto YouTube News Summarizer workflow.

    Args:
        args: Command-line arguments

    Returns:
        True if the workflow completed successfully, False otherwise
    """
    try:
        logger.info("Starting Crypto YouTube News Summarizer workflow")

        search_queries = args.search_queries or config.SEARCH_QUERIES

        youtube_api = YouTubeAPI()
        video_downloader = VideoDownloader()
        transcript_extractor = TranscriptExtractor()
        content_summarizer = ContentSummarizer()
        report_generator = ReportGenerator()
        email_sender = EmailSender()

        if args.email_recipient:
            email_sender.recipient_email = args.email_recipient

        channels = find_crypto_channels(
            youtube_api, search_queries, args.max_channels)

        if not channels:
            logger.warning("No crypto YouTube channels found")
            return False

        all_summaries = []
        for channel in channels:
            channel_id = channel['id']
            channel_title = channel['title']

            logger.info(
                f"Processing channel: {channel_title} (ID: {channel_id})")

            if args.skip_download:
                logger.info(
                    f"Skipping video download for channel: {channel_title}")
                videos = []
            else:
                videos = download_channel_videos(
                    youtube_api,
                    video_downloader,
                    channel,
                    args.videos_per_channel
                )

            if not videos:
                logger.warning(
                    f"No videos to process for channel: {channel_title}")
                continue

            summaries = process_videos(
                transcript_extractor, content_summarizer, videos)

            if summaries:
                all_summaries.extend(summaries)
                logger.info(
                    f"Added {
                        len(summaries)} summaries for channel: {channel_title}")
            else:
                logger.warning(
                    f"No summaries generated for channel: {channel_title}")

        if not all_summaries:
            logger.warning("No summaries generated for any channel")
            return False

        logger.info(
            f"Generating comprehensive report with {
                len(all_summaries)} summaries")
        report_generator.generate_report(all_summaries)
        text_report_path = report_generator.generate_text_report(all_summaries)

        if not args.skip_email:
            logger.info("Sending email report")

            attachments = []
            if text_report_path:
                attachments.append(text_report_path)

            email_success = email_sender.send_summary_report(
                summaries=all_summaries,
                attachments=attachments
            )

            if email_success:
                logger.info("Email report sent successfully")
            else:
                logger.error("Failed to send email report")
                return False
        else:
            logger.info("Skipping email report")

        logger.info(
            "Crypto YouTube News Summarizer workflow completed successfully")
        return True

    except Exception as e:
        logger.error(
            f"Error running Crypto YouTube News Summarizer workflow: {e}",
            exc_info=True)
        return False


def main():
    """Main function to run the Crypto YouTube News Summarizer."""
    try:
        args = parse_arguments()

        logger.info("Starting Crypto YouTube News Summarizer")

        if args.schedule:
            logger.info(
                f"Running in scheduled mode with interval: {
                    args.schedule_interval} hours")

            scheduler = Scheduler(interval_hours=args.schedule_interval)
            scheduler.start(run_workflow, args)

            try:
                next_run = scheduler.get_next_run()
                logger.info(f"Next run scheduled for: {next_run}")

                logger.info("Press Ctrl+C to stop the scheduler")
                while True:
                    time.sleep(60)

            except KeyboardInterrupt:
                logger.info("Stopping scheduler")
                scheduler.stop()
                logger.info("Scheduler stopped")
        else:
            run_workflow(args)

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")

    except Exception as e:
        logger.error(
            f"Error running Crypto YouTube News Summarizer: {e}",
            exc_info=True)


if __name__ == "__main__":
    main()
