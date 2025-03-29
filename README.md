# Crypto YouTube News Summarizer

This Python application automates the process of finding cryptocurrency-focused YouTube channels, downloading their recent videos, summarizing the content, and emailing comprehensive reports.

## Features

- **YouTube Channel Discovery**: Automatically identifies YouTube channels focused on cryptocurrency topics
- **Video Download**: Downloads recent videos from identified channels
- **Content Extraction**: Extracts transcripts from videos
- **Content Summarization**: Uses NLP to generate concise summaries of video content
- **Report Generation**: Aggregates summaries into comprehensive reports
- **Email Delivery**: Sends formatted reports to specified email addresses

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
   - Add your YouTube API key, email credentials, and other settings

## Usage

Run the main script to execute the complete workflow:

```bash
python crypto_news_summarizer.py
```

### Configuration Options

Edit `config.py` to customize:
- Number of videos to download per channel
- Search criteria for YouTube channels
- Email settings
- Summarization parameters

## Requirements

- Python 3.8+
- YouTube Data API key
- Email account for sending reports

## License

MIT
