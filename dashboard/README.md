# Pharmaceutical News Dashboard

A modern, responsive dashboard for visualizing pharmaceutical news data collected by the monitoring system.

## Features

- **Dashboard Overview**: Key metrics, topic distribution, and recent articles
- **Article Explorer**: Browse, search, and filter classified articles
- **Analytics**: Visualize trends, topic patterns, and confidence distributions
- **Insights**: AI-powered recommendations and system performance analysis

## Tech Stack

- **Framework**: SvelteKit
- **Styling**: Tailwind CSS + DaisyUI
- **Charts**: Chart.js
- **Icons**: Lucide Svelte
- **Deployment**: GitHub Pages

## Development

1. Install dependencies:
```bash
npm install
```

2. Copy data files and run development server:
```bash
npm run copy-data
npm run dev
```

3. Build for production:
```bash
./build.sh
```

## Deployment

The dashboard is automatically deployed to GitHub Pages when changes are pushed to the main branch.

Manual deployment:
```bash
npm run build
# Deploy the 'build' directory to your hosting service
```

## Data Format

The dashboard expects JSON files in the `/data` directory with the following structure:
```json
{
  "run_timestamp": "ISO date string",
  "total_articles_fetched": number,
  "total_articles_classified": number,
  "articles": [...]
}
```

## Components

- **Layout**: Header, Sidebar, Toast notifications
- **Dashboard**: MetricCard, TopicChart, SourceChart, RecentArticles
- **Articles**: ArticleCard, ArticleDetail, ArticleFilters
- **Charts**: Various Chart.js-based visualizations
- **Common**: SearchBar, LoadingSpinner, Badge

## Performance

- Lazy loading for article content
- Debounced search functionality
- Optimized chart rendering
- Responsive design for all screen sizes