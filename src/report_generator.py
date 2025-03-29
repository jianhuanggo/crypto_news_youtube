"""
Module for generating reports from video summaries.
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Class for generating reports from video summaries."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = output_dir
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created report directory: {self.output_dir}")
    
    def generate_report(self, summaries: List[Dict[str, Any]], report_title: str = "Crypto YouTube Summary Report") -> Optional[str]:
        """
        Generate a comprehensive report from video summaries.
        
        Args:
            summaries: List of summary information dictionaries
            report_title: Title of the report
            
        Returns:
            Path to the generated report file or None if generation failed
        """
        if not summaries:
            logger.warning("No summaries provided for the report")
            return None
        
        try:
            report_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            report_filename = f"crypto_report_{report_date}.html"
            report_path = os.path.join(self.output_dir, report_filename)
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{report_title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
                    header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                    h1 {{ margin: 0; }}
                    .report-meta {{ background-color: #f8f9fa; padding: 10px; margin: 20px 0; border-radius: 5px; }}
                    .channel-section {{ margin-bottom: 40px; }}
                    .channel-header {{ background-color: #3498db; color: white; padding: 10px; border-radius: 5px; }}
                    .video-summary {{ margin: 20px 0; border-left: 4px solid #3498db; padding-left: 15px; }}
                    .video-title {{ font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
                    .video-meta {{ font-size: 14px; color: #7f8c8d; margin-bottom: 10px; }}
                    .video-summary-text {{ margin-top: 10px; }}
                    .video-link {{ color: #3498db; text-decoration: none; }}
                    .video-link:hover {{ text-decoration: underline; }}
                    .footer {{ margin-top: 40px; font-size: 12px; color: #7f8c8d; border-top: 1px solid #eee; padding-top: 10px; text-align: center; }}
                </style>
            </head>
            <body>
                <header>
                    <h1>{report_title}</h1>
                </header>
                <div class="container">
                    <div class="report-meta">
                        <p><strong>Report generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                        <p><strong>Total videos summarized:</strong> {len(summaries)}</p>
                    </div>
            """
            
            channels = {}
            for summary in summaries:
                channel_id = summary.get('channel_id')
                channel_title = summary.get('channel_title', 'Unknown Channel')
                
                if channel_id not in channels:
                    channels[channel_id] = {
                        'title': channel_title,
                        'videos': []
                    }
                
                channels[channel_id]['videos'].append(summary)
            
            for channel_id, channel_data in channels.items():
                channel_title = channel_data['title']
                videos = channel_data['videos']
                
                html_content += f"""
                    <div class="channel-section">
                        <div class="channel-header">
                            <h2>{channel_title}</h2>
                        </div>
                """
                
                for video in videos:
                    video_title = video.get('title', 'Untitled Video')
                    video_url = video.get('url', '#')
                    published_at = video.get('published_at', 'Unknown date')
                    view_count = video.get('view_count', 'N/A')
                    like_count = video.get('like_count', 'N/A')
                    duration = video.get('duration', 'Unknown duration')
                    summary_text = video.get('summary', 'No summary available')
                    
                    html_content += f"""
                        <div class="video-summary">
                            <div class="video-title">
                                <a href="{video_url}" class="video-link" target="_blank">{video_title}</a>
                            </div>
                            <div class="video-meta">
                                Published: {published_at} | Duration: {duration} | Views: {view_count} | Likes: {like_count}
                            </div>
                            <div class="video-summary-text">
                                <p>{summary_text}</p>
                            </div>
                        </div>
                    """
                
                html_content += """
                    </div>
                """
            
            html_content += """
                    <div class="footer">
                        <p>This report was automatically generated by the Crypto YouTube News Summarizer.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated report saved to: {report_path}")
            
            json_path = os.path.join(self.output_dir, f"crypto_report_{report_date}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(summaries, f, indent=2)
            
            logger.info(f"JSON data saved to: {json_path}")
            
            return report_path
        
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None
    
    def generate_text_report(self, summaries: List[Dict[str, Any]], report_title: str = "Crypto YouTube Summary Report") -> Optional[str]:
        """
        Generate a plain text report from video summaries.
        
        Args:
            summaries: List of summary information dictionaries
            report_title: Title of the report
            
        Returns:
            Path to the generated text report file or None if generation failed
        """
        if not summaries:
            logger.warning("No summaries provided for the text report")
            return None
        
        try:
            report_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            report_filename = f"crypto_report_{report_date}.txt"
            report_path = os.path.join(self.output_dir, report_filename)
            
            text_content = f"{report_title}\n"
            text_content += "=" * len(report_title) + "\n\n"
            text_content += f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            text_content += f"Total videos summarized: {len(summaries)}\n\n"
            
            channels = {}
            for summary in summaries:
                channel_id = summary.get('channel_id')
                channel_title = summary.get('channel_title', 'Unknown Channel')
                
                if channel_id not in channels:
                    channels[channel_id] = {
                        'title': channel_title,
                        'videos': []
                    }
                
                channels[channel_id]['videos'].append(summary)
            
            for channel_id, channel_data in channels.items():
                channel_title = channel_data['title']
                videos = channel_data['videos']
                
                text_content += f"\n\n{channel_title}\n"
                text_content += "-" * len(channel_title) + "\n\n"
                
                for video in videos:
                    video_title = video.get('title', 'Untitled Video')
                    video_url = video.get('url', '#')
                    published_at = video.get('published_at', 'Unknown date')
                    view_count = video.get('view_count', 'N/A')
                    duration = video.get('duration', 'Unknown duration')
                    summary_text = video.get('summary', 'No summary available')
                    
                    text_content += f"Title: {video_title}\n"
                    text_content += f"URL: {video_url}\n"
                    text_content += f"Published: {published_at} | Duration: {duration} | Views: {view_count}\n\n"
                    text_content += f"Summary:\n{summary_text}\n\n"
                    text_content += "----------------------------------------\n\n"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            logger.info(f"Generated text report saved to: {report_path}")
            return report_path
        
        except Exception as e:
            logger.error(f"Error generating text report: {e}")
            return None
