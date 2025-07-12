<script>
  import { onMount } from 'svelte';
  import { 
    FileText, 
    TrendingUp, 
    Filter, 
    CheckCircle,
    Activity,
    Zap
  } from 'lucide-svelte';
  import MetricCard from '$lib/components/dashboard/MetricCard.svelte';
  import TopicChart from '$lib/components/dashboard/TopicChart.svelte';
  import SourceChart from '$lib/components/dashboard/SourceChart.svelte';
  import RecentArticles from '$lib/components/dashboard/RecentArticles.svelte';
  import PerformanceMetrics from '$lib/components/dashboard/PerformanceMetrics.svelte';
  import LoadingSpinner from '$lib/components/common/LoadingSpinner.svelte';
  import { 
    monitoringRuns, 
    allArticles, 
    topicDistribution,
    isLoading,
    loadError
  } from '$lib/stores/articles';
  
  let totalFetched = 0;
  let totalClassified = 0;
  let totalDiscarded = 0;
  let avgClassificationRate = 0;
  
  $: if ($monitoringRuns.length > 0) {
    totalFetched = $monitoringRuns.reduce((sum, run) => sum + (run.total_articles_fetched || 0), 0);
    totalClassified = $monitoringRuns.reduce((sum, run) => sum + (run.total_articles_classified || 0), 0);
    totalDiscarded = $monitoringRuns.reduce((sum, run) => sum + (run.total_articles_discarded || 0), 0);
    avgClassificationRate = totalFetched > 0 ? (totalClassified / totalFetched) * 100 : 0;
  }
</script>

<svelte:head>
  <title>Dashboard - Pharma News Monitor</title>
</svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-3xl font-bold mb-2">Dashboard Overview</h1>
    <p class="text-base-content/60">
      Monitor pharmaceutical news trends and insights in real-time
    </p>
  </div>

  {#if $isLoading}
    <LoadingSpinner size="lg" />
  {:else if $loadError}
    <div class="alert alert-error">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{$loadError}</span>
    </div>
  {:else}
    <!-- Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        title="Total Articles Fetched"
        value={totalFetched.toLocaleString()}
        subtitle="Across {$monitoringRuns.length} monitoring runs"
        icon={FileText}
        delay={0}
      />
      
      <MetricCard
        title="Articles Classified"
        value={totalClassified.toLocaleString()}
        subtitle="{avgClassificationRate.toFixed(1)}% classification rate"
        icon={CheckCircle}
        trend={{ value: avgClassificationRate.toFixed(0), isPositive: avgClassificationRate > 15 }}
        delay={100}
      />
      
      <MetricCard
        title="Topics Tracked"
        value={$topicDistribution.length}
        subtitle="Unique pharmaceutical topics"
        icon={Filter}
        delay={200}
      />
      
      <MetricCard
        title="Performance Gain"
        value="82%"
        subtitle="Fewer web requests needed"
        icon={Zap}
        trend={{ value: 82, isPositive: true }}
        delay={300}
      />
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <TopicChart />
      <SourceChart />
    </div>

    <!-- Recent Articles and Performance -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2">
        <RecentArticles />
      </div>
      <div>
        <PerformanceMetrics />
      </div>
    </div>
  {/if}
</div>