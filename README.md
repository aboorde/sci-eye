# Pharmaceutical News Monitoring System

An intelligent news aggregation and classification system for pharmaceutical industry professionals with optimized performance.

## Features

- **RSS Feed Aggregation**: Monitors multiple pharmaceutical news sources
- **AI-Powered Classification**: Automatically categorizes articles by relevant topics
- **Smart Filtering**: Classifies articles BEFORE scraping to save time and resources
- **Content Summarization**: Generates concise summaries of full articles
- **Structured Storage**: Saves processed data in JSON format for analysis

## Optimized Workflow

1. **Fetch RSS Feeds** - Quick retrieval of article metadata
2. **Classify First** - AI classification based on title/description only
3. **Filter Early** - Discard irrelevant articles before expensive operations
4. **Scrape Selectively** - Only fetch full content for classified articles
5. **Summarize & Store** - Generate summaries and save to JSON

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"

```

3. Run the script:

```bash
python pharma_news_monitor.py
```

## Monitored Topics

The system classifies articles into topics including:

- Orphan Drug Designation
- FDA Accelerated Approval
- Clinical trial results
- Drug approvals
- Safety concerns
- Market authorizations
- And more...

## Output

Processed articles are saved as JSON files in the `data/` directory with:

- Article summaries
- Classification topics
- Confidence scores
- Source information
- Processing timestamps

## Configuration

Edit the `CONFIG` dictionary in `pharma_news_monitor.py` to:

- Add/remove RSS feeds
- Modify classification topics
- Adjust AI model settings

## RSS Feeds

Currently monitoring:

- FierceBiotech
- FiercePharma
- Evaluate Vantage

## Performance Benefits

The optimized workflow provides significant improvements:

- **80%+ faster** processing for typical RSS feeds
- **Reduced web requests** by only scraping relevant articles
- **Lower costs** from fewer API calls and bandwidth usage
- **Better reliability** with fewer failed scraping attempts

## Data Structure

Output files contain a single array of classified articles per run:

```json
{
  "run_timestamp": "2025-01-12T14:35:21.847293",
  "total_articles_fetched": 45,
  "total_articles_classified": 8,
  "total_articles_discarded": 37,
  "classification_rate": "17.8%",
  "configuration": {...},
  "articles": [
    {
      "id": "unique_identifier",
      "title": "Article Title",
      "summary": "AI-generated summary",
      "topics": ["FDA Approval", "Clinical Trial"],
      "confidence_scores": {...},
      "link": "article_url",
      "date_processed": "timestamp",
      "has_full_content": true
    }
  ]
}
```

## Performance Demo

Run the performance demonstration:

```bash
python demo_performance.py
```

This shows the time and resource savings from the optimized workflow.

## Validation

Test the classification system before running:

```bash
python validate_classification.py
```

This ensures the AI classification is working correctly with sample articles.

## Dashboard

View your pharmaceutical news data in a beautiful web dashboard:

### Features

- **Real-time Analytics**: Topic trends, source distribution, and performance metrics
- **Article Explorer**: Search, filter, and read classified articles
- **AI Insights**: Get recommendations to optimize your monitoring
- **Responsive Design**: Works on desktop, tablet, and mobile

### Running the Dashboard

1. Navigate to the dashboard directory:

```bash
cd dashboard
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

4. Open http://localhost:5173 in your browser

### Deployment

The dashboard can be automatically deployed to GitHub Pages:

1. Push changes to the main branch
2. GitHub Actions will build and deploy automatically
3. Access at: https://[your-username].github.io/sci-eye/

### Building for Production

```bash
cd dashboard
./build.sh
```
