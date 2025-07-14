import { writable, derived } from 'svelte/store';
import { loadAllData, aggregateArticles } from '$lib/utils/dataLoader';
import { 
  calculateTopicDistribution, 
  calculateSourceDistribution,
  filterArticles,
  getTrendingTopics,
  calculateDailyMetrics
} from '$lib/utils/dataProcessor';

// Raw monitoring runs data
export const monitoringRuns = writable([]);

// Filters store
function createFiltersStore() {
  const { subscribe, set, update } = writable({
    topics: [],
    sources: [],
    startDate: null,
    endDate: null,
    minConfidence: null,
    searchQuery: ''
  });

  return {
    subscribe,
    setTopics: (topics) => update(f => ({ ...f, topics })),
    setSources: (sources) => update(f => ({ ...f, sources })),
    setDateRange: (startDate, endDate) => update(f => ({ ...f, startDate, endDate })),
    setMinConfidence: (minConfidence) => update(f => ({ ...f, minConfidence })),
    setSearchQuery: (searchQuery) => update(f => ({ ...f, searchQuery })),
    reset: () => set({
      topics: [],
      sources: [],
      startDate: null,
      endDate: null,
      minConfidence: null,
      searchQuery: ''
    })
  };
}

export const filters = createFiltersStore();

// All articles aggregated from runs
export const allArticles = derived(
  monitoringRuns,
  $runs => {
    const articles = aggregateArticles($runs);
    // Sort by published date (newest first)
    return articles.sort((a, b) => {
      const dateA = new Date(a.date_published || a.date_processed);
      const dateB = new Date(b.date_published || b.date_processed);
      return dateB - dateA;
    });
  }
);

// Filtered articles based on current filters
export const filteredArticles = derived(
  [allArticles, filters],
  ([$articles, $filters]) => {
    const filtered = filterArticles($articles, $filters);
    // Sort by published date (newest first)
    return filtered.sort((a, b) => {
      const dateA = new Date(a.date_published || a.date_processed);
      const dateB = new Date(b.date_published || b.date_processed);
      return dateB - dateA;
    });
  }
);

// Topic distribution
export const topicDistribution = derived(
  filteredArticles,
  $articles => calculateTopicDistribution($articles)
);

// Source distribution
export const sourceDistribution = derived(
  filteredArticles,
  $articles => calculateSourceDistribution($articles)
);

// Trending topics
export const trendingTopics = derived(
  allArticles,
  $articles => getTrendingTopics($articles, 7)
);

// Daily metrics
export const dailyMetrics = derived(
  monitoringRuns,
  $runs => calculateDailyMetrics($runs)
);

// Chart time range
export const chartTimeRange = writable('30d');

// Loading state
export const isLoading = writable(true);

// Error state
export const loadError = writable(null);

// Initialize data
export async function initializeData() {
  isLoading.set(true);
  loadError.set(null);
  
  try {
    const data = await loadAllData();
    monitoringRuns.set(data);
  } catch (error) {
    console.error('Failed to load data:', error);
    loadError.set('Failed to load monitoring data. Please try again.');
  } finally {
    isLoading.set(false);
  }
}