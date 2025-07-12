<script>
  import { Calendar } from 'lucide-svelte';
  import LoadingSpinner from '$lib/components/common/LoadingSpinner.svelte';
  import DailyTrendsChart from '$lib/components/charts/DailyTrendsChart.svelte';
  import TopicTrendsChart from '$lib/components/charts/TopicTrendsChart.svelte';
  import ConfidenceDistribution from '$lib/components/charts/ConfidenceDistribution.svelte';
  import WordCloud from '$lib/components/charts/WordCloud.svelte';
  import { 
    isLoading, 
    chartTimeRange,
    dailyMetrics,
    trendingTopics
  } from '$lib/stores/articles';
  
  const timeRanges = [
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' },
    { value: 'all', label: 'All Time' }
  ];
</script>

<svelte:head>
  <title>Analytics - Pharma News Monitor</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
    <div>
      <h1 class="text-3xl font-bold mb-2">Analytics</h1>
      <p class="text-base-content/60">
        Analyze trends and patterns in pharmaceutical news
      </p>
    </div>
    
    <!-- Time Range Selector -->
    <div class="flex items-center gap-2">
      <Calendar size={16} class="text-base-content/60" />
      <select 
        class="select select-bordered select-sm"
        bind:value={$chartTimeRange}
      >
        {#each timeRanges as range}
          <option value={range.value}>{range.label}</option>
        {/each}
      </select>
    </div>
  </div>

  {#if $isLoading}
    <LoadingSpinner size="lg" />
  {:else}
    <!-- Trending Topics -->
    {#if $trendingTopics.length > 0}
      <div class="glass-card rounded-xl p-6">
        <h2 class="text-lg font-semibold mb-4">Trending Topics</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each $trendingTopics.slice(0, 6) as topic}
            <div class="bg-base-200/50 rounded-lg p-4">
              <h3 class="font-medium mb-2">{topic.topic}</h3>
              <div class="flex items-center justify-between">
                <span class="text-2xl font-bold">{topic.count}</span>
                <div class="text-right">
                  <span 
                    class="text-sm font-medium {topic.growth > 0 ? 'text-success' : topic.growth < 0 ? 'text-error' : 'text-base-content/50'}"
                  >
                    {topic.growth > 0 ? '+' : ''}{topic.growth.toFixed(1)}%
                  </span>
                  <p class="text-xs text-base-content/50">vs. previous period</p>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
    
    <!-- Charts Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <DailyTrendsChart />
      <TopicTrendsChart />
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ConfidenceDistribution />
      <WordCloud />
    </div>
  {/if}
</div>