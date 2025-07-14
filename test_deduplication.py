#!/usr/bin/env python3
"""Test script to verify deduplication is working properly."""

import json
from pathlib import Path

def test_deduplication():
    """Test the deduplication functionality."""
    # Check if index file exists
    index_path = Path("data/article_index.json")
    
    if index_path.exists():
        with open(index_path, 'r') as f:
            index_data = json.load(f)
            
        print(f"Article Index Summary:")
        print(f"- Last updated: {index_data.get('last_updated', 'N/A')}")
        print(f"- Total unique articles tracked: {index_data.get('total_articles', 0)}")
        print(f"- Sample article IDs: {index_data.get('article_ids', [])[:5]}")
    else:
        print("No article index found yet. Run the monitor first.")
        
    # Check latest run for duplicate statistics
    data_dir = Path("data")
    json_files = sorted(data_dir.glob("pharma_news_*.json"), reverse=True)
    
    if json_files:
        latest_file = json_files[0]
        print(f"\nLatest run: {latest_file.name}")
        
        with open(latest_file, 'r') as f:
            run_data = json.load(f)
            
        print(f"Run Statistics:")
        print(f"- Total articles fetched: {run_data.get('total_articles_fetched', 0)}")
        print(f"- Duplicates skipped: {run_data.get('total_duplicates_skipped', 0)}")
        print(f"- Unique articles: {run_data.get('total_unique_articles', 0)}")
        print(f"- Articles classified: {run_data.get('total_articles_classified', 0)}")
        print(f"- Articles discarded: {run_data.get('total_articles_discarded', 0)}")
        print(f"- Classification rate: {run_data.get('classification_rate', 'N/A')}")

if __name__ == "__main__":
    test_deduplication()