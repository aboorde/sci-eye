import { format, parseISO, startOfDay, differenceInDays } from 'date-fns';

/**
 * Calculate topic distribution across all articles
 * @param {Array} articles - Array of articles
 * @returns {Object} Topic counts and percentages
 */
export function calculateTopicDistribution(articles) {
  const topicCounts = {};
  const total = articles.length;

  for (const article of articles) {
    for (const topic of article.topics || []) {
      topicCounts[topic] = (topicCounts[topic] || 0) + 1;
    }
  }

  const distribution = Object.entries(topicCounts)
    .map(([topic, count]) => ({
      topic,
      count,
      percentage: (count / total) * 100
    }))
    .sort((a, b) => b.count - a.count);

  return distribution;
}

/**
 * Calculate source distribution
 * @param {Array} articles - Array of articles
 * @returns {Object} Source counts and percentages
 */
export function calculateSourceDistribution(articles) {
  const sourceCounts = {};
  const total = articles.length;

  for (const article of articles) {
    const source = article.source_feed || 'Unknown';
    sourceCounts[source] = (sourceCounts[source] || 0) + 1;
  }

  const distribution = Object.entries(sourceCounts)
    .map(([source, count]) => ({
      source,
      count,
      percentage: (count / total) * 100
    }))
    .sort((a, b) => b.count - a.count);

  return distribution;
}

/**
 * Calculate average confidence scores by topic
 * @param {Array} articles - Array of articles
 * @returns {Object} Average confidence by topic
 */
export function calculateAverageConfidence(articles) {
  const topicConfidence = {};
  const topicCounts = {};

  for (const article of articles) {
    const scores = article.confidence_scores || {};
    for (const [topic, score] of Object.entries(scores)) {
      if (!topicConfidence[topic]) {
        topicConfidence[topic] = 0;
        topicCounts[topic] = 0;
      }
      topicConfidence[topic] += score;
      topicCounts[topic] += 1;
    }
  }

  const averages = Object.entries(topicConfidence)
    .map(([topic, total]) => ({
      topic,
      averageConfidence: total / topicCounts[topic],
      count: topicCounts[topic]
    }))
    .sort((a, b) => b.averageConfidence - a.averageConfidence);

  return averages;
}

/**
 * Group articles by date
 * @param {Array} articles - Array of articles
 * @returns {Object} Articles grouped by date
 */
export function groupArticlesByDate(articles) {
  const grouped = {};

  for (const article of articles) {
    let date = 'Unknown';
    
    if (article.date_published) {
      try {
        // Parse the date_published string (e.g., "Jul 11, 2025 11:43am")
        const parsedDate = new Date(article.date_published);
        if (!isNaN(parsedDate.getTime())) {
          date = format(parsedDate, 'yyyy-MM-dd');
        }
      } catch (e) {
        // If parsing fails, fallback to date_processed
        if (article.date_processed) {
          date = format(parseISO(article.date_processed), 'yyyy-MM-dd');
        }
      }
    } else if (article.date_processed) {
      date = format(parseISO(article.date_processed), 'yyyy-MM-dd');
    }
    
    if (!grouped[date]) {
      grouped[date] = [];
    }
    grouped[date].push(article);
  }

  return grouped;
}

/**
 * Calculate daily metrics over time
 * @param {Array} runs - Array of monitoring runs
 * @returns {Array} Daily metrics
 */
export function calculateDailyMetrics(runs) {
  const dailyData = {};

  for (const run of runs) {
    const date = format(parseISO(run.run_timestamp), 'yyyy-MM-dd');
    
    if (!dailyData[date]) {
      dailyData[date] = {
        date,
        totalFetched: 0,
        totalClassified: 0,
        totalDiscarded: 0,
        runs: 0
      };
    }

    dailyData[date].totalFetched += run.total_articles_fetched || 0;
    dailyData[date].totalClassified += run.total_articles_classified || 0;
    dailyData[date].totalDiscarded += run.total_articles_discarded || 0;
    dailyData[date].runs += 1;
  }

  return Object.values(dailyData)
    .map(day => ({
      ...day,
      classificationRate: day.totalFetched > 0 ? 
        (day.totalClassified / day.totalFetched) * 100 : 0
    }))
    .sort((a, b) => a.date.localeCompare(b.date));
}

/**
 * Get recent articles
 * @param {Array} articles - Array of articles
 * @param {number} days - Number of days to look back
 * @returns {Array} Recent articles
 */
export function getRecentArticles(articles, days = 7) {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);

  return articles.filter(article => {
    if (!article.date_processed) return false;
    const articleDate = parseISO(article.date_processed);
    return articleDate >= cutoffDate;
  });
}

/**
 * Get trending topics
 * @param {Array} articles - Array of articles
 * @param {number} recentDays - Days to consider as "recent"
 * @returns {Array} Trending topics with growth rate
 */
export function getTrendingTopics(articles, recentDays = 7) {
  const recent = getRecentArticles(articles, recentDays);
  const older = articles.filter(a => !recent.includes(a));

  const recentTopics = calculateTopicDistribution(recent);
  const olderTopics = calculateTopicDistribution(older);

  const olderTopicsMap = Object.fromEntries(
    olderTopics.map(t => [t.topic, t.percentage])
  );

  const trending = recentTopics.map(topic => {
    const oldPercentage = olderTopicsMap[topic.topic] || 0;
    const growth = topic.percentage - oldPercentage;
    
    return {
      ...topic,
      growth,
      growthRate: oldPercentage > 0 ? 
        ((topic.percentage - oldPercentage) / oldPercentage) * 100 : 
        100
    };
  }).sort((a, b) => b.growth - a.growth);

  return trending;
}

/**
 * Filter articles by criteria
 * @param {Array} articles - Array of articles
 * @param {Object} filters - Filter criteria
 * @returns {Array} Filtered articles
 */
export function filterArticles(articles, filters = {}) {
  let filtered = [...articles];

  // Filter by topics
  if (filters.topics && filters.topics.length > 0) {
    filtered = filtered.filter(article => 
      article.topics.some(topic => filters.topics.includes(topic))
    );
  }

  // Filter by sources
  if (filters.sources && filters.sources.length > 0) {
    filtered = filtered.filter(article => 
      filters.sources.includes(article.source_feed)
    );
  }

  // Filter by date range
  if (filters.startDate) {
    const start = parseISO(filters.startDate);
    filtered = filtered.filter(article => 
      article.date_processed && parseISO(article.date_processed) >= start
    );
  }

  if (filters.endDate) {
    const end = parseISO(filters.endDate);
    filtered = filtered.filter(article => 
      article.date_processed && parseISO(article.date_processed) <= end
    );
  }

  // Filter by minimum confidence
  if (filters.minConfidence) {
    filtered = filtered.filter(article => {
      const scores = Object.values(article.confidence_scores || {});
      return scores.length > 0 && Math.max(...scores) >= filters.minConfidence;
    });
  }

  // Filter by search query
  if (filters.searchQuery) {
    const query = filters.searchQuery.toLowerCase();
    filtered = filtered.filter(article => 
      article.title.toLowerCase().includes(query) ||
      article.summary.toLowerCase().includes(query) ||
      article.original_description.toLowerCase().includes(query)
    );
  }

  return filtered;
}