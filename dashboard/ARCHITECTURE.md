# Pharmaceutical News Dashboard - Architecture Plan

## Overview
A modern, responsive dashboard for viewing and analyzing pharmaceutical news data collected by the monitoring system.

## Technology Stack
- **Framework**: SvelteKit (for static site generation)
- **Styling**: Tailwind CSS + DaisyUI (component library)
- **Charts**: Chart.js with chartjs-plugin-datalabels
- **Icons**: Lucide Svelte
- **Animations**: Svelte transitions + Tailwind animations
- **State Management**: Svelte stores
- **Build**: Vite
- **Deployment**: GitHub Pages via GitHub Actions

## Features

### 1. Dashboard Overview
- Total articles tracked
- Classification rate trends
- Topic distribution pie chart
- Recent articles timeline
- Source distribution
- Performance metrics

### 2. Article Explorer
- Grid/List view toggle
- Advanced filtering (topics, sources, dates, confidence)
- Full-text search
- Article cards with summaries
- Detailed article modal
- Export functionality

### 3. Analytics
- Topic trends over time
- Source reliability metrics
- Classification confidence distribution
- Word cloud of common terms
- Daily/Weekly/Monthly views

### 4. Data Insights
- Top performing topics
- Emerging trends detection
- Low confidence articles for review
- Source comparison

## Component Structure

```
src/
├── lib/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.svelte
│   │   │   ├── Sidebar.svelte
│   │   │   └── Footer.svelte
│   │   ├── dashboard/
│   │   │   ├── MetricCard.svelte
│   │   │   ├── TopicChart.svelte
│   │   │   ├── SourceChart.svelte
│   │   │   ├── RecentArticles.svelte
│   │   │   └── PerformanceMetrics.svelte
│   │   ├── articles/
│   │   │   ├── ArticleCard.svelte
│   │   │   ├── ArticleGrid.svelte
│   │   │   ├── ArticleList.svelte
│   │   │   ├── ArticleDetail.svelte
│   │   │   └── ArticleFilters.svelte
│   │   ├── charts/
│   │   │   ├── PieChart.svelte
│   │   │   ├── LineChart.svelte
│   │   │   ├── BarChart.svelte
│   │   │   └── WordCloud.svelte
│   │   └── common/
│   │       ├── SearchBar.svelte
│   │       ├── DatePicker.svelte
│   │       ├── Badge.svelte
│   │       └── LoadingSpinner.svelte
│   ├── stores/
│   │   ├── articles.js
│   │   ├── filters.js
│   │   └── ui.js
│   ├── utils/
│   │   ├── dataLoader.js
│   │   ├── dataProcessor.js
│   │   ├── chartHelpers.js
│   │   └── formatters.js
│   └── data/
│       └── (JSON files copied here during build)
├── routes/
│   ├── +layout.svelte
│   ├── +page.svelte (Dashboard)
│   ├── articles/+page.svelte
│   ├── analytics/+page.svelte
│   └── insights/+page.svelte
└── app.html
```

## Data Flow
1. Build process copies JSON files to static directory
2. DataLoader fetches all JSON files on app load
3. DataProcessor aggregates and transforms data
4. Svelte stores manage application state
5. Components subscribe to stores for reactive updates

## Visual Design
- **Color Scheme**: Professional blues and grays with accent colors for topics
- **Typography**: Inter for UI, Source Serif Pro for article content
- **Layout**: Responsive grid with collapsible sidebar
- **Dark Mode**: Toggle between light/dark themes
- **Animations**: Smooth transitions, loading states, hover effects

## Performance Optimizations
- Lazy loading for article content
- Virtual scrolling for large lists
- Debounced search
- Memoized calculations
- Progressive data loading

## Deployment Strategy
1. GitHub Actions workflow triggered on push
2. Build SvelteKit app as static site
3. Deploy to GitHub Pages with proper base path
4. Enable caching for static assets