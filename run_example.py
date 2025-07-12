#!/usr/bin/env python3
"""
Example script showing how to use the Pharmaceutical News Monitor
and analyze the stored data.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def run_monitor():
    """Run the news monitor if API key is set."""
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable first!")
        print("Example: export OPENAI_API_KEY='your-key-here'")
        return False
    
    print("Running pharmaceutical news monitor...")
    os.system("python pharma_news_monitor.py")
    return True

def analyze_stored_data():
    """Analyze JSON files in the data directory."""
    data_dir = Path("data")
    if not data_dir.exists():
        print("No data directory found. Run the monitor first.")
        return
    
    json_files = list(data_dir.glob("pharma_news_*.json"))
    if not json_files:
        print("No data files found. Run the monitor first.")
        return
    
    print(f"\nAnalyzing {len(json_files)} monitoring runs...")
    
    # Aggregate statistics across all runs
    topic_counts = defaultdict(int)
    source_counts = defaultdict(int)
    all_articles = []
    total_fetched = 0
    total_classified = 0
    
    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.loads(f.read())
            
            # Update totals
            total_fetched += data.get('total_articles_fetched', 0)
            total_classified += data.get('total_articles_classified', 0)
            
            # Process articles from this run
            for article in data.get('articles', []):
                all_articles.append(article)
                
                # Count topics
                for topic in article.get('topics', []):
                    topic_counts[topic] += 1
                
                # Count sources
                source_counts[article.get('source_feed', 'Unknown')] += 1
    
    # Display analysis
    print(f"\nTotal articles fetched across all runs: {total_fetched}")
    print(f"Total articles classified: {total_classified}")
    print(f"Classification rate: {total_classified/total_fetched*100:.1f}%" if total_fetched > 0 else "N/A")
    
    print("\n=== TOPIC ANALYSIS ===")
    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{topic}: {count} articles")
    
    print("\n=== SOURCE ANALYSIS ===")
    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{source}: {count} articles")
    
    # Show recent high-confidence articles
    print("\n=== RECENT HIGH-CONFIDENCE ARTICLES ===")
    sorted_articles = sorted(all_articles, 
                           key=lambda x: x.get('date_processed', ''), 
                           reverse=True)[:5]
    
    for article in sorted_articles:
        print(f"\nTitle: {article['title']}")
        print(f"Topics: {', '.join(article.get('topics', []))}")
        print(f"Link: {article['link']}")
        if article.get('confidence_scores'):
            max_topic = max(article['confidence_scores'].items(), 
                          key=lambda x: x[1])
            print(f"Highest confidence: {max_topic[0]} ({max_topic[1]:.2f})")

def search_by_topic(topic_keyword):
    """Search stored articles by topic keyword."""
    data_dir = Path("data")
    if not data_dir.exists():
        print("No data directory found.")
        return
    
    matching_articles = []
    
    for json_file in data_dir.glob("pharma_news_*.json"):
        with open(json_file, 'r') as f:
            data = json.loads(f.read())
            
            # Search through articles in this run
            for article in data.get('articles', []):
                # Check if any topic contains the keyword
                for topic in article.get('topics', []):
                    if topic_keyword.lower() in topic.lower():
                        matching_articles.append(article)
                        break
    
    print(f"\nFound {len(matching_articles)} articles matching '{topic_keyword}':")
    for article in matching_articles[:10]:  # Show first 10
        print(f"\n- {article['title']}")
        print(f"  Topics: {', '.join(article['topics'])}")
        print(f"  Date: {article.get('date_published', 'Unknown')}")

if __name__ == "__main__":
    print("Pharmaceutical News Monitor - Example Usage")
    print("=" * 50)
    
    # Option 1: Run the monitor
    print("\n1. Running the news monitor...")
    if run_monitor():
        print("Monitor completed successfully!")
    
    # Option 2: Analyze stored data
    print("\n2. Analyzing stored data...")
    analyze_stored_data()
    
    # Option 3: Search by topic
    print("\n3. Searching for FDA-related articles...")
    search_by_topic("FDA")
    
    print("\n\nTo run just the monitor: python pharma_news_monitor.py")
    print("To analyze data only: python run_example.py (after setting analyze_only=True)")