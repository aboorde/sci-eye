#!/usr/bin/env python3
"""
Pharmaceutical News Monitoring System
Aggregates RSS feeds, classifies articles by topic, and generates summaries.

Optimized workflow:
1. Fetch RSS feeds
2. Classify articles based on title/description (fast)
3. Discard irrelevant articles
4. Scrape and summarize only classified articles
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import feedparser
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import cloudscraper
from newspaper import Article
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
def load_config():
    """Load configuration from file or use defaults."""
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
            # Add headers if not present
            if 'scraping' in config and 'headers' not in config['scraping']:
                config['scraping']['headers'] = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache"
                }
            return config
    else:
        # Default configuration
        return {
        "rss_feeds": [
            {
            "url": "https://www.fiercebiotech.com/rss/xml",
            "name": "FierceBiotech"
            },
            {
            "url": "https://www.fiercepharma.com/rss/xml", 
            "name": "FiercePharma"
            },
            {
            "url": "https://www.biopharmadive.com/feeds/news/",
            "name": "BioPharma Dive"
            },
            {
            "url": "https://www.pharmtech.com/rss",
            "name": "Pharmaceutical Technology"
            }
        ],
        "topics": [
            "Orphan Drug Designation",
            "Interim analysis were positive",
            "FDA Accelerated Approval",
            "Clinical trial results",
            "Drug approval",
            "Safety concerns",
            "Market authorization",
            "Phase 3 trial",
            "Phase 2 trial",
            "Breakthrough therapy designation",
            "EMA approval",
            "Patent expiration",
            "Biosimilar approval",
            "Merger and acquisition",
            "FDA Complete Response Letter",
            "Priority review",
            "Fast track designation",
            "New drug application",
            "Biologics license application",
            "Advisory committee meeting",
            "Label expansion",
            "Pricing and reimbursement",
            "Real-world evidence"
        ],
        "ai_settings": {
            "model": "gpt-4.1-nano",
            "classification_temperature": 0.3,
            "summary_temperature": 0.5,
            "max_summary_tokens": 700,
            "classification_threshold": 0.7
        },
        "scraping": {
            "timeout": 30,
            "max_retries": 3,
            "rate_limit_delay": 1,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
        },
        "processing": {
            "parallel_classification": true,
            "max_classification_workers": 5,
            "batch_classification_size": 5
        }
        }
CONFIG = load_config()


class PharmaNewsMonitor:
    def __init__(self, api_key: str):
        """Initialize the news monitor with OpenAI API key."""
        self.client = OpenAI(api_key=api_key)
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.total_articles_fetched = 0
        self.total_articles_discarded = 0
        self.total_duplicates_skipped = 0
        # Create a session for better cookie handling
        self.session = requests.Session()
        self.session.headers.update(CONFIG["scraping"]["headers"])
        # Initialize deduplication system
        self.seen_articles = set()
        self.dedup_index_path = self.data_dir / "article_index.json"
        self._load_article_index()
        
    def _load_article_index(self):
        """Load the article index from disk to track seen articles."""
        if self.dedup_index_path.exists():
            try:
                with open(self.dedup_index_path, 'r') as f:
                    index_data = json.load(f)
                    self.seen_articles = set(index_data.get('article_ids', []))
                    logger.info(f"Loaded {len(self.seen_articles)} article IDs from index")
            except Exception as e:
                logger.error(f"Error loading article index: {e}")
                self.seen_articles = set()
        else:
            logger.info("No existing article index found, starting fresh")
            
    def _save_article_index(self):
        """Save the article index to disk."""
        try:
            index_data = {
                'last_updated': datetime.now().isoformat(),
                'total_articles': len(self.seen_articles),
                'article_ids': list(self.seen_articles)
            }
            with open(self.dedup_index_path, 'w') as f:
                json.dump(index_data, f, indent=2)
            logger.info(f"Saved article index with {len(self.seen_articles)} IDs")
        except Exception as e:
            logger.error(f"Error saving article index: {e}")
            
    def _generate_article_id(self, article: Dict) -> str:
        """Generate a unique ID for an article based on URL and title."""
        # Primary: Use URL if available
        if article.get('link'):
            return hashlib.md5(article['link'].encode()).hexdigest()
        # Fallback: Use title + source
        else:
            content = f"{article.get('title', '')}_{article.get('source_feed', '')}"
            return hashlib.md5(content.encode()).hexdigest()
            
    def _is_duplicate(self, article: Dict) -> bool:
        """Check if an article is a duplicate based on its ID."""
        article_id = self._generate_article_id(article)
        return article_id in self.seen_articles
        
    def _mark_as_seen(self, article: Dict):
        """Mark an article as seen by adding its ID to the index."""
        article_id = self._generate_article_id(article)
        self.seen_articles.add(article_id)
        
    def fetch_rss_feeds(self) -> List[Dict]:
        """Fetch and parse all configured RSS feeds."""
        all_articles = []
        duplicate_count = 0
        
        for feed_config in CONFIG["rss_feeds"]:
            try:
                logger.info(f"Fetching RSS feed: {feed_config['name']}")
                feed = feedparser.parse(feed_config['url'])
                feed_articles_count = 0
                feed_duplicates_count = 0
                
                for entry in feed.entries:
                    # Try to get full content from RSS if available
                    full_content_rss = None
                    if hasattr(entry, 'content'):
                        # Some feeds include full content
                        full_content_rss = entry.content[0].get('value', '') if entry.content else ''
                    elif hasattr(entry, 'content_encoded'):
                        full_content_rss = entry.content_encoded
                    
                    article = {
                        "title": entry.get("title", ""),
                        "description": entry.get("description", entry.get("summary", "")),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "source_feed": feed_config['name'],
                        "feed_url": feed_config['url'],
                        "full_content_rss": full_content_rss  # Store RSS content if available
                    }
                    
                    # Check for duplicates
                    if self._is_duplicate(article):
                        duplicate_count += 1
                        feed_duplicates_count += 1
                        logger.debug(f"Skipping duplicate: {article['title'][:60]}...")
                    else:
                        all_articles.append(article)
                        feed_articles_count += 1
                    
                logger.info(f"Fetched {len(feed.entries)} articles from {feed_config['name']}: {feed_articles_count} new, {feed_duplicates_count} duplicates")
                
            except Exception as e:
                logger.error(f"Error fetching feed {feed_config['name']}: {str(e)}")
        
        self.total_articles_fetched = len(all_articles) + duplicate_count
        self.total_duplicates_skipped = duplicate_count
        
        if duplicate_count > 0:
            logger.info(f"Total duplicates skipped: {duplicate_count}")
            
        return all_articles
    
    def classify_article(self, article: Dict) -> Tuple[List[str], Dict[str, float]]:
        """Classify an article based on predefined topics using AI."""
        try:
            threshold = CONFIG.get('ai_settings', {}).get('classification_threshold', 0.7)
            prompt = f"""
            Analyze the following pharmaceutical news article and identify which of these topics it DIRECTLY and EXPLICITLY relates to.
            Be VERY strict - only classify an article under a topic if it is clearly and directly about that specific topic.
            
            Article Title: {article['title']}
            Article Description: {article['description']}
            
            Topics to consider:
            {', '.join(CONFIG['topics'])}
            
            Classification guidelines for 100% confidence:
            - "Success in preclinical study": ONLY if explicitly states successful preclinical results
            - "Orphan drug designation": ONLY if explicitly states FDA/EMA granted orphan drug designation
            - "Series B fundraising complete": ONLY if explicitly announces completion of Series B funding round
            - "Interim analysis results were positive": ONLY if explicitly states positive interim analysis with specific data
            - "FDA Accelerated Approval": ONLY if explicitly states FDA granted accelerated approval
            - "Breakthrough therapy designation": ONLY if explicitly states FDA granted breakthrough therapy designation
            
            Requirements for 100% confidence:
            - The exact phrase or very close variant must be present
            - The action must be completed (not planned or hoped for)
            - The information must be the main focus of the article
            - DO NOT infer or interpret - only explicit statements count
            
            Return your response as a JSON object with two keys:
            - "topics": list of relevant topic names from the list above
            - "confidence": dictionary mapping each identified topic to a confidence score (0.0-1.0)
            
            Only include topics with PERFECT confidence of 1.0 (100% certain).
            If you are not 100% certain about a topic, DO NOT include it.
            """
            
            response = self.client.chat.completions.create(
                model=CONFIG["ai_settings"]["model"],
                messages=[
                    {"role": "system", "content": "You are a pharmaceutical industry expert who classifies news articles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=CONFIG["ai_settings"]["classification_temperature"],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            topics = result.get("topics", [])
            confidence = result.get("confidence", {})
            
            return topics, confidence
            
        except Exception as e:
            logger.error(f"Error classifying article '{article['title']}': {str(e)}")
            return [], {}
    
    def scrape_article_content(self, url: str) -> Optional[str]:
        """Scrape the full content of an article from its URL using multiple methods."""
        # Add delay to be respectful to servers
        time.sleep(CONFIG["scraping"].get("rate_limit_delay", 1))
        
        # Method 1: Try newspaper3k first (handles many edge cases)
        content = self._try_newspaper(url)
        if content:
            return content
            
        # Method 2: Try cloudscraper (handles Cloudflare)
        content = self._try_cloudscraper(url)
        if content:
            return content
            
        # Method 3: Try standard requests with session
        content = self._try_requests(url)
        if content:
            return content
            
        # Method 4: Try httpx as last resort
        content = self._try_httpx(url)
        if content:
            return content
            
        logger.warning(f"All methods failed to scrape {url}")
        return None
    
    def _try_newspaper(self, url: str) -> Optional[str]:
        """Try scraping with newspaper3k library."""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            if article.text and len(article.text) > 100:
                logger.info(f"✓ Successfully scraped with newspaper3k")
                # Limit content length
                content = article.text
                if len(content) > 10000:
                    content = content[:10000] + "..."
                return content
        except Exception as e:
            logger.debug(f"Newspaper3k failed: {str(e)}")
        return None
    
    def _try_cloudscraper(self, url: str) -> Optional[str]:
        """Try scraping with cloudscraper (handles Cloudflare)."""
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url, timeout=CONFIG["scraping"]["timeout"])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content = self._extract_content_from_soup(soup)
            
            if content and len(content) > 100:
                logger.info(f"✓ Successfully scraped with cloudscraper")
                return content
        except Exception as e:
            logger.debug(f"Cloudscraper failed: {str(e)}")
        return None
    
    def _try_requests(self, url: str) -> Optional[str]:
        """Try scraping with standard requests."""
        try:
            response = self.session.get(
                url,
                timeout=CONFIG["scraping"]["timeout"],
                allow_redirects=True,
                verify=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content = self._extract_content_from_soup(soup)
            
            if content and len(content) > 100:
                logger.info(f"✓ Successfully scraped with requests")
                return content
        except Exception as e:
            logger.debug(f"Requests failed: {str(e)}")
        return None
    
    def _try_httpx(self, url: str) -> Optional[str]:
        """Try scraping with httpx."""
        try:
            with httpx.Client(follow_redirects=True) as client:
                response = client.get(
                    url,
                    headers=CONFIG["scraping"]["headers"],
                    timeout=CONFIG["scraping"]["timeout"]
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                content = self._extract_content_from_soup(soup)
                
                if content and len(content) > 100:
                    logger.info(f"✓ Successfully scraped with httpx")
                    return content
        except Exception as e:
            logger.debug(f"Httpx failed: {str(e)}")
        return None
    
    def _extract_content_from_soup(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article content from BeautifulSoup object."""
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Try different content selectors
        content_selectors = [
            'article',
            '[class*="article-content"]',
            '[class*="article-body"]',
            '[class*="post-content"]',
            '[class*="entry-content"]',
            '[class*="story-body"]',
            '[class*="content-body"]',
            '.content',
            'main',
            '[role="main"]'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                article_content = content.get_text(separator=' ', strip=True)
                if article_content and len(article_content) > 100:
                    # Clean up the text
                    article_content = ' '.join(article_content.split())
                    
                    # Limit content length
                    if len(article_content) > 10000:
                        article_content = article_content[:10000] + "..."
                    
                    return article_content
        
        # Fallback to body if no specific content found
        if soup.body:
            article_content = soup.body.get_text(separator=' ', strip=True)
            article_content = ' '.join(article_content.split())
            
            if len(article_content) > 500:  # Only use body if substantial content
                if len(article_content) > 10000:
                    article_content = article_content[:10000] + "..."
                return article_content
        
        return None
    
    def generate_summary(self, article: Dict, full_content: Optional[str]) -> str:
        """Generate a summary of the article using AI."""
        try:
            content_to_summarize = full_content if full_content else article['description']
            
            prompt = f"""
            Create a concise summary of this pharmaceutical news article for industry professionals.
            Focus on key facts, implications, and relevance to the pharmaceutical industry.
            
            Title: {article['title']}
            Content: {content_to_summarize}
            
            Provide a 2-3 paragraph summary highlighting:
            1. Main news/announcement
            2. Key details and implications
            3. Relevance to the pharmaceutical industry
            """
            
            response = self.client.chat.completions.create(
                model=CONFIG["ai_settings"]["model"],
                messages=[
                    {"role": "system", "content": "You are a pharmaceutical industry analyst creating concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=CONFIG["ai_settings"]["summary_temperature"],
                max_tokens=CONFIG["ai_settings"]["max_summary_tokens"]
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary for '{article['title']}': {str(e)}")
            return article['description']
    
    def save_processed_articles(self, articles: List[Dict]) -> str:
        """Save all processed articles to a single JSON file."""
        # Generate unique filename for this run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pharma_news_{timestamp}.json"
        filepath = self.data_dir / filename
        
        # Create output structure
        unique_articles = self.total_articles_fetched - self.total_duplicates_skipped
        output_data = {
            "run_timestamp": datetime.now().isoformat(),
            "total_articles_fetched": self.total_articles_fetched,
            "total_duplicates_skipped": self.total_duplicates_skipped,
            "total_unique_articles": unique_articles,
            "total_articles_classified": len(articles),
            "total_articles_discarded": self.total_articles_discarded,
            "classification_rate": f"{(len(articles) / unique_articles * 100):.1f}%" if unique_articles > 0 else "0%",
            "configuration": {
                "feeds": [feed["name"] for feed in CONFIG["rss_feeds"]],
                "topics_monitored": len(CONFIG["topics"]),
                "classification_threshold": CONFIG.get("ai_settings", {}).get("classification_threshold", 0.7)
            },
            "articles": articles
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Saved {len(articles)} articles to {filepath}")
        return str(filepath)
    
    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process all articles: classify first, then scrape and summarize only classified articles."""
        classified_articles = []
        discarded_count = 0
        
        # Phase 1: Classification (fast, no web scraping)
        logger.info(f"\n=== Phase 1: Classifying {len(articles)} articles ===")
        for i, article in enumerate(articles):
            logger.info(f"Classifying {i+1}/{len(articles)}: {article['title'][:80]}...")
            
            # Classify based on RSS title and description only
            topics, confidence_scores = self.classify_article(article)
            
            if topics:
                logger.info(f"✓ Classified with topics: {', '.join(topics)}")
                classified_articles.append({
                    'article': article,
                    'topics': topics,
                    'confidence_scores': confidence_scores
                })
            else:
                logger.debug(f"✗ No relevant topics found, discarding article")
                discarded_count += 1
        
        logger.info(f"\nClassification complete: {len(classified_articles)} relevant, {discarded_count} discarded")
        self.total_articles_discarded = discarded_count
        
        if not classified_articles:
            logger.info("No articles matched the classification criteria.")
            return []
        
        # Phase 2: Scraping and summarization (only for classified articles)
        logger.info(f"\n=== Phase 2: Processing {len(classified_articles)} classified articles ===")
        processed_articles = []
        
        for i, item in enumerate(classified_articles):
            article = item['article']
            topics = item['topics']
            confidence_scores = item['confidence_scores']
            
            logger.info(f"\nProcessing {i+1}/{len(classified_articles)}: {article['title'][:80]}...")
            logger.info(f"Topics: {', '.join(topics)}")
            
            # Try to get full content
            full_content = None
            
            # First check if RSS feed already has full content
            if article.get('full_content_rss'):
                # Clean HTML from RSS content
                soup = BeautifulSoup(article['full_content_rss'], 'html.parser')
                rss_content = soup.get_text(separator=' ', strip=True)
                rss_content = ' '.join(rss_content.split())
                
                if len(rss_content) > 500:  # Substantial content
                    full_content = rss_content
                    logger.info("✓ Using full content from RSS feed")
            
            # If no RSS content, try scraping
            if not full_content and article['link']:
                logger.info(f"Scraping full content from: {article['link']}")
                full_content = self.scrape_article_content(article['link'])
                if full_content:
                    logger.info("✓ Successfully scraped full content")
                else:
                    logger.warning("✗ Failed to scrape full content, will use RSS description")
            
            # Generate summary (using full content if available, otherwise RSS description)
            logger.info("Generating AI summary...")
            summary = self.generate_summary(article, full_content)
            
            # Prepare data for storage
            article_data = {
                "id": self._generate_article_id(article),
                "title": article['title'],
                "original_description": article['description'],
                "summary": summary,
                "link": article['link'],
                "topics": topics,
                "confidence_scores": confidence_scores,
                "date_published": article['published'],
                "date_processed": datetime.now().isoformat(),
                "source_feed": article['source_feed'],
                "has_full_content": full_content is not None
            }
            
            processed_articles.append(article_data)
            # Mark article as seen for future deduplication
            self._mark_as_seen(article)
            
            # Rate limiting between web scraping
            if i < len(classified_articles) - 1:  # Don't sleep after last article
                time.sleep(CONFIG.get('scraping', {}).get('rate_limit_delay', 1))
            
        return processed_articles
    
    def run(self):
        """Main execution method."""
        logger.info("Starting Pharmaceutical News Monitor")
        
        # Fetch RSS feeds
        logger.info("Fetching RSS feeds...")
        articles = self.fetch_rss_feeds()
        logger.info(f"Total articles fetched: {len(articles)}")
        
        # Process articles
        logger.info("Processing articles...")
        processed = self.process_articles(articles)
        
        # Save all processed articles to a single file
        if processed:
            filepath = self.save_processed_articles(processed)
            logger.info(f"\nProcessing complete! Results saved to: {filepath}")
        else:
            logger.info("\nNo articles matched the classification criteria.")
        
        # Save the article index for future deduplication
        self._save_article_index()
        
        # Summary report
        logger.info("\n=== FINAL SUMMARY ===")
        logger.info(f"Total articles fetched: {self.total_articles_fetched}")
        logger.info(f"Total duplicates skipped: {self.total_duplicates_skipped}")
        logger.info(f"Total unique articles processed: {self.total_articles_fetched - self.total_duplicates_skipped}")
        logger.info(f"Total articles classified: {len(processed)}")
        logger.info(f"Total articles discarded: {self.total_articles_discarded}")
        logger.info(f"Classification rate: {len(processed)/(self.total_articles_fetched - self.total_duplicates_skipped)*100:.1f}%" if (self.total_articles_fetched - self.total_duplicates_skipped) > 0 else "N/A")
        
        # Print topic distribution
        topic_counts = {}
        for article in processed:
            for topic in article['topics']:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        if topic_counts:
            logger.info("\nTopic distribution:")
            for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {topic}: {count} articles")
        
        return processed


def main():
    """Main entry point."""
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("Please set the OPENAI_API_KEY environment variable in your .env file")
        logger.error("Copy .env.example to .env and add your OpenAI API key")
        return
    
    # Create and run monitor
    monitor = PharmaNewsMonitor(api_key)
    monitor.run()


if __name__ == "__main__":
    main()