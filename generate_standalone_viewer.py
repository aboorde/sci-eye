#!/usr/bin/env python3
"""
Generate a standalone HTML file with embedded pharmaceutical news data
that can be opened directly in a browser without any server.
"""

import json
import os
from datetime import datetime

def generate_standalone_viewer(json_file_path, output_path="pharma_news_standalone.html"):
    """Generate a self-contained HTML file with embedded data."""
    
    # Read the JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract articles (handle both formats)
    if isinstance(data, list):
        articles = data
        metadata = {
            "run_timestamp": datetime.now().isoformat(),
            "total_articles": len(data)
        }
    else:
        articles = data.get('articles', [])
        metadata = {k: v for k, v in data.items() if k != 'articles'}
    
    # Read the template
    with open('pharma_news_viewer.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Replace the placeholder with actual data
    # Find the line with EMBEDDED_DATA and replace it
    embedded_data_line = "        const EMBEDDED_DATA = null; // This will be replaced when generating the file with data"
    replacement_line = f"        const EMBEDDED_DATA = {json.dumps(articles, indent=2, ensure_ascii=False)};"
    
    # Also add metadata
    metadata_line = f"        const METADATA = {json.dumps(metadata, indent=2, ensure_ascii=False)};"
    
    # Replace in template
    output_html = template.replace(embedded_data_line, replacement_line + "\n" + metadata_line)
    
    # Update the title to include the date
    if 'run_timestamp' in metadata:
        date_str = metadata['run_timestamp'][:10]
        output_html = output_html.replace(
            "<title>Pharmaceutical News Intelligence</title>",
            f"<title>Pharmaceutical News Intelligence - {date_str}</title>"
        )
    
    # Write the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_html)
    
    # Get file size
    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
    
    print(f"✅ Generated standalone viewer: {output_path}")
    print(f"📊 File size: {file_size:.2f} MB")
    print(f"📰 Articles included: {len(articles)}")
    print(f"\n📤 You can now send this file to anyone!")
    print("They can simply double-click to open it in their browser.")

if __name__ == "__main__":
    # Find the most recent JSON file
    import glob
    
    json_files = glob.glob('data/pharma_news_*.json')
    if json_files:
        latest_file = max(json_files)
        print(f"Using latest data file: {latest_file}")
        generate_standalone_viewer(latest_file)
    else:
        print("No data files found in data/ directory")