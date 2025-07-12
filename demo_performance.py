#!/usr/bin/env python3
"""
Performance demonstration script showing the improvements from the refactored workflow.
Shows how early classification saves time and resources.
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path

def simulate_monitor_run():
    """Simulate a monitoring run with timing information."""
    print("=== Pharmaceutical News Monitor - Performance Demo ===\n")
    
    # Simulated metrics
    total_articles = 45
    classified_articles = 8
    discarded_articles = total_articles - classified_articles
    
    # Timing estimates
    classification_time_per_article = 0.5  # seconds
    scraping_time_per_article = 3.0  # seconds
    summary_time_per_article = 2.0  # seconds
    
    print("🔍 OPTIMIZED WORKFLOW (New Version):")
    print(f"   1. Fetching {total_articles} articles from RSS feeds...")
    time.sleep(1)
    
    print(f"\n   2. Classification Phase (Title/Description only):")
    classification_time = total_articles * classification_time_per_article
    print(f"      - Processing {total_articles} articles")
    print(f"      - Time: {classification_time:.1f} seconds")
    print(f"      - Results: {classified_articles} relevant, {discarded_articles} discarded")
    
    print(f"\n   3. Web Scraping Phase (Only classified articles):")
    scraping_time = classified_articles * scraping_time_per_article
    print(f"      - Scraping {classified_articles} articles")
    print(f"      - Time: {scraping_time:.1f} seconds")
    print(f"      - Saved: {discarded_articles * scraping_time_per_article:.1f} seconds by not scraping irrelevant articles!")
    
    print(f"\n   4. Summarization Phase:")
    summary_time = classified_articles * summary_time_per_article
    print(f"      - Summarizing {classified_articles} articles")
    print(f"      - Time: {summary_time:.1f} seconds")
    
    total_optimized_time = classification_time + scraping_time + summary_time
    
    print(f"\n📊 COMPARISON WITH OLD WORKFLOW:")
    print(f"   Old workflow (classify after scraping all):")
    old_time = total_articles * (classification_time_per_article + scraping_time_per_article) + classified_articles * summary_time_per_article
    print(f"   - Total time: {old_time:.1f} seconds")
    
    print(f"\n   New workflow (classify first, scrape only relevant):")
    print(f"   - Total time: {total_optimized_time:.1f} seconds")
    
    time_saved = old_time - total_optimized_time
    improvement_percentage = (time_saved / old_time) * 100
    
    print(f"\n✨ PERFORMANCE IMPROVEMENT:")
    print(f"   - Time saved: {time_saved:.1f} seconds")
    print(f"   - Improvement: {improvement_percentage:.1f}% faster")
    print(f"   - Web requests reduced by: {discarded_articles} ({discarded_articles/total_articles*100:.1f}%)")
    
    print(f"\n💰 COST SAVINGS:")
    print(f"   - API calls saved: {discarded_articles} web scraping requests")
    print(f"   - Bandwidth saved: ~{discarded_articles * 50}KB (estimated)")
    
    # Create example output
    create_example_output(total_articles, classified_articles, discarded_articles)

def create_example_output(total, classified, discarded):
    """Create an example output file showing the new format."""
    output_data = {
        "run_timestamp": datetime.now().isoformat(),
        "total_articles_fetched": total,
        "total_articles_classified": classified,
        "total_articles_discarded": discarded,
        "classification_rate": f"{(classified / total * 100):.1f}%",
        "performance_metrics": {
            "classification_phase_duration": "22.5 seconds",
            "scraping_phase_duration": "24.0 seconds",
            "summary_phase_duration": "16.0 seconds",
            "total_duration": "62.5 seconds",
            "web_requests_saved": discarded
        },
        "configuration": {
            "feeds": ["FierceBiotech", "FiercePharma", "Evaluate Vantage", "BioPharma Dive", "Pharmaceutical Technology"],
            "topics_monitored": 25,
            "classification_threshold": 0.7
        },
        "articles": [
            {
                "id": "demo123",
                "title": "FDA Grants Priority Review for Novel Cancer Immunotherapy",
                "original_description": "The FDA has accepted and granted Priority Review to the Biologics License Application for a novel checkpoint inhibitor...",
                "summary": "The FDA has granted Priority Review to a groundbreaking cancer immunotherapy that showed exceptional results in Phase 3 trials...",
                "link": "https://example.com/article1",
                "topics": ["Priority review", "Drug approval", "Clinical trial results"],
                "confidence_scores": {
                    "Priority review": 0.98,
                    "Drug approval": 0.92,
                    "Clinical trial results": 0.88
                },
                "date_published": "Fri, 12 Jan 2025 10:00:00 GMT",
                "date_processed": datetime.now().isoformat(),
                "source_feed": "FierceBiotech",
                "has_full_content": True
            }
        ]
    }
    
    # Save demo output
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pharma_news_demo_{timestamp}.json"
    filepath = data_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 Demo output saved to: {filepath}")

if __name__ == "__main__":
    simulate_monitor_run()
    
    print("\n" + "="*60)
    print("To run the actual monitor: python pharma_news_monitor.py")
    print("="*60)