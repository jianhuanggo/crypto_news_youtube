"""
Configuration settings for the Crypto YouTube News Summarizer.
Copy this file to config.py and update with your own settings.
"""

YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"

SEARCH_QUERIES = [
    "crypto news",
    "cryptocurrency analysis",
    "bitcoin news",
    "ethereum news",
    "crypto market analysis"
]
MAX_SEARCH_RESULTS = 10  # Number of channels to find per search query
CHANNEL_RELEVANCE_THRESHOLD = 0.7  # Threshold for determining if a channel is crypto-focused (0-1)

VIDEOS_PER_CHANNEL = 5  # Number of recent videos to download per channel
MIN_VIDEO_LENGTH_SECONDS = 300  # Minimum video length (5 minutes)
MAX_VIDEO_LENGTH_SECONDS = 1800  # Maximum video length (30 minutes)
DOWNLOAD_DIR = "downloads"  # Directory to store downloaded videos

SUMMARY_MIN_LENGTH = 100  # Minimum length of summary in words
SUMMARY_MAX_LENGTH = 300  # Maximum length of summary in words
SUMMARIZATION_MODEL = "facebook/bart-large-cnn"  # HuggingFace model for summarization

EMAIL_SENDER = "your_email@example.com"
EMAIL_PASSWORD = "your_app_password"  # Use app password for Gmail
EMAIL_RECIPIENT = "recipient@example.com"
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587

SCHEDULE_INTERVAL = 24  # Run the script every 24 hours
