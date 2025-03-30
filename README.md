# Crypto YouTube News Summarizer

This Python application automates the process of finding cryptocurrency-focused YouTube channels, downloading their recent videos, summarizing the content, and emailing comprehensive reports.

## Features

- **YouTube Channel Discovery**: Automatically identifies YouTube channels focused on cryptocurrency topics
- **Video Download**: Downloads recent videos from identified channels
- **Content Extraction**: Extracts transcripts from videos
- **Content Summarization**: Uses NLP to generate concise summaries of video content
- **Report Generation**: Aggregates summaries into comprehensive reports
- **Email Delivery**: Sends formatted reports to specified email addresses
- **Scheduled Execution**: Runs the workflow automatically at configurable intervals

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jianhuanggo/crypto_news_youtube.git
cd crypto_news_youtube
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your configuration:
   - Copy `config_example.py` to `config.py`
   - Add your YouTube API key (get one from [Google Cloud Console](https://console.cloud.google.com/))
   - Configure email credentials (for Gmail, use an [App Password](https://support.google.com/accounts/answer/185833))
   - Adjust other settings as needed

## Usage

### Basic Usage

Run the main script to execute the complete workflow:

```bash
python crypto_news_summarizer.py
```

### Command-line Arguments

The application supports various command-line arguments for customization:

```bash
# Specify custom search queries
python crypto_news_summarizer.py --search-queries "bitcoin news" "ethereum analysis"

# Limit the number of channels to process
python crypto_news_summarizer.py --max-channels 5

# Set the number of videos to download per channel
python crypto_news_summarizer.py --videos-per-channel 3

# Skip the download step (use existing downloads)
python crypto_news_summarizer.py --skip-download

# Skip sending email
python crypto_news_summarizer.py --skip-email

# Send email to a specific recipient
python crypto_news_summarizer.py --email-recipient user@example.com

# Run on a schedule
python crypto_news_summarizer.py --schedule

# Set custom schedule interval (in hours)
python crypto_news_summarizer.py --schedule --schedule-interval 12
```

### Scheduled Execution

To run the application on a schedule:

```bash
# Run every 24 hours (default)
python crypto_news_summarizer.py --schedule

# Run every 12 hours
python crypto_news_summarizer.py --schedule --schedule-interval 12
```

When running in scheduled mode, the application will:
1. Execute the workflow immediately
2. Schedule the next run based on the specified interval
3. Continue running until interrupted (Ctrl+C)

## Configuration

### YouTube API Configuration

In your `config.py` file:

```python
# Your YouTube Data API key
YOUTUBE_API_KEY = "your_api_key_here"

# Search queries for finding crypto channels
SEARCH_QUERIES = [
    "crypto news",
    "cryptocurrency analysis",
    "bitcoin news"
]

# Number of channels to find per search query
MAX_SEARCH_RESULTS = 10

# Threshold for determining if a channel is crypto-focused (0-1)
CHANNEL_RELEVANCE_THRESHOLD = 0.7
```

### Video Download Configuration

```python
# Number of recent videos to download per channel
VIDEOS_PER_CHANNEL = 5

# Minimum video length (5 minutes)
MIN_VIDEO_LENGTH_SECONDS = 300

# Maximum video length (30 minutes)
MAX_VIDEO_LENGTH_SECONDS = 1800

# Directory to store downloaded videos
DOWNLOAD_DIR = "downloads"
```

### Summarization Configuration

```python
# Minimum length of summary in words
SUMMARY_MIN_LENGTH = 100

# Maximum length of summary in words
SUMMARY_MAX_LENGTH = 300

# HuggingFace model for summarization
SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
```

### Email Configuration

```python
# Email sender address
EMAIL_SENDER = "your_email@example.com"

# Email password or app password
EMAIL_PASSWORD = "your_app_password"

# Email recipient address
EMAIL_RECIPIENT = "recipient@example.com"

# SMTP server settings
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
```

### Scheduling Configuration

```python
# Run the script every 24 hours
SCHEDULE_INTERVAL = 24
```

## Troubleshooting

### YouTube API Issues

- **API Key Invalid**: Ensure your YouTube API key is correct and has the YouTube Data API v3 enabled
- **Quota Exceeded**: The YouTube API has daily quotas. If exceeded, wait until the quota resets or use a different API key

### Video Download Issues

- **Download Failures**: Some videos may be unavailable or restricted. The application will log these and continue with available videos
- **No Videos Found**: Ensure your search queries are relevant and the MAX_SEARCH_RESULTS is set appropriately

### Transcript Issues

- **Missing Transcripts**: Some videos may not have transcripts available. The application will log these and continue with videos that have transcripts
- **Transcript Language**: By default, the application tries to get English transcripts. Modify the code if you need other languages

### Email Issues

- **Authentication Failures**: For Gmail, ensure you're using an App Password, not your regular password
- **Connection Issues**: Check your internet connection and firewall settings
- **SMTP Settings**: Verify the SMTP server and port settings for your email provider

## Requirements

- Python 3.8+
- YouTube Data API key
- Email account for sending reports
- Internet connection

## License

MIT
