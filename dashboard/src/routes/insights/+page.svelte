<script>
  import { TrendingUp, AlertCircle, Target, Lightbulb } from 'lucide-svelte';
  import LoadingSpinner from '$lib/components/common/LoadingSpinner.svelte';
  import { 
    isLoading,
    monitoringRuns,
    allArticles,
    topicDistribution,
    trendingTopics
  } from '$lib/stores/articles';
  import { formatPercentage } from '$lib/utils/formatters';
  
  $: insights = generateInsights();
  
  function generateInsights() {
    if ($allArticles.length === 0) return [];
    
    const insights = [];
    
    // Performance insights
    const avgClassificationRate = calculateAvgClassificationRate();
    if (avgClassificationRate < 10) {
      insights.push({
        type: 'warning',
        icon: AlertCircle,
        title: 'Low Classification Rate',
        description: `Only ${avgClassificationRate.toFixed(1)}% of articles are being classified. Consider adjusting topics or lowering the confidence threshold.`,
        metric: `${avgClassificationRate.toFixed(1)}%`
      });
    }
    
    // Trending topic insights
    const topTrending = $trendingTopics.filter(t => t.growth > 50);
    if (topTrending.length > 0) {
      insights.push({
        type: 'success',
        icon: TrendingUp,
        title: 'Rapidly Growing Topics',
        description: `${topTrending.map(t => t.topic).join(', ')} ${topTrending.length === 1 ? 'is' : 'are'} seeing significant growth in coverage.`,
        metric: `+${Math.max(...topTrending.map(t => t.growth)).toFixed(0)}%`
      });
    }
    
    // Topic concentration
    const topicConcentration = calculateTopicConcentration();
    if (topicConcentration > 0.5) {
      const topTopic = $topicDistribution[0];
      insights.push({
        type: 'info',
        icon: Target,
        title: 'High Topic Concentration',
        description: `"${topTopic.topic}" accounts for ${topicConcentration.toFixed(0)}% of all classified articles, indicating a strong focus area.`,
        metric: `${topicConcentration.toFixed(0)}%`
      });
    }
    
    // Source diversity
    const sourceDiversity = calculateSourceDiversity();
    if (sourceDiversity < 3) {
      insights.push({
        type: 'warning',
        icon: Lightbulb,
        title: 'Limited Source Diversity',
        description: 'Consider adding more RSS feeds to get a broader perspective on pharmaceutical news.',
        metric: `${sourceDiversity} sources`
      });
    }
    
    // Low confidence articles
    const lowConfidenceCount = countLowConfidenceArticles();
    if (lowConfidenceCount > $allArticles.length * 0.2) {
      insights.push({
        type: 'warning',
        icon: AlertCircle,
        title: 'Many Low Confidence Classifications',
        description: `${lowConfidenceCount} articles have confidence scores below 80%. Review these for potential misclassifications.`,
        metric: `${lowConfidenceCount} articles`
      });
    }
    
    return insights;
  }
  
  function calculateAvgClassificationRate() {
    if ($monitoringRuns.length === 0) return 0;
    
    const totalFetched = $monitoringRuns.reduce((sum, run) => sum + (run.total_articles_fetched || 0), 0);
    const totalClassified = $monitoringRuns.reduce((sum, run) => sum + (run.total_articles_classified || 0), 0);
    
    return totalFetched > 0 ? (totalClassified / totalFetched) * 100 : 0;
  }
  
  function calculateTopicConcentration() {
    if ($topicDistribution.length === 0) return 0;
    return ($topicDistribution[0].count / $allArticles.length) * 100;
  }
  
  function calculateSourceDiversity() {
    const sources = new Set($allArticles.map(a => a.source_feed));
    return sources.size;
  }
  
  function countLowConfidenceArticles() {
    return $allArticles.filter(article => {
      const scores = Object.values(article.confidence_scores || {});
      return scores.length > 0 && Math.max(...scores) < 0.8;
    }).length;
  }
  
  const insightColors = {
    success: 'border-success bg-success/10',
    warning: 'border-warning bg-warning/10',
    info: 'border-info bg-info/10',
    error: 'border-error bg-error/10'
  };
  
  const iconColors = {
    success: 'text-success',
    warning: 'text-warning',
    info: 'text-info',
    error: 'text-error'
  };
</script>

<svelte:head>
  <title>Insights - Pharma News Monitor</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div>
    <h1 class="text-3xl font-bold mb-2">Insights & Recommendations</h1>
    <p class="text-base-content/60">
      AI-powered insights to optimize your pharmaceutical news monitoring
    </p>
  </div>

  {#if $isLoading}
    <LoadingSpinner size="lg" />
  {:else if insights.length === 0}
    <div class="text-center py-16">
      <p class="text-lg text-base-content/50">
        No insights available yet. Run more monitoring sessions to generate insights.
      </p>
    </div>
  {:else}
    <!-- Insights Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      {#each insights as insight, i}
        <div 
          class="glass-card rounded-xl p-6 border-l-4 {insightColors[insight.type]} animate-fade-in"
          style="animation-delay: {i * 100}ms"
        >
          <div class="flex items-start gap-4">
            <div class="p-3 rounded-lg bg-base-200/50">
              <svelte:component 
                this={insight.icon} 
                size={24} 
                class={iconColors[insight.type]}
              />
            </div>
            
            <div class="flex-1">
              <h3 class="font-semibold mb-2">{insight.title}</h3>
              <p class="text-sm text-base-content/70 mb-3">
                {insight.description}
              </p>
              
              {#if insight.metric}
                <div class="inline-flex items-center px-3 py-1 rounded-full bg-base-200/50">
                  <span class="text-sm font-medium">{insight.metric}</span>
                </div>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>
    
    <!-- Summary Stats -->
    <div class="glass-card rounded-xl p-6">
      <h2 class="text-lg font-semibold mb-4">System Performance Summary</h2>
      
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center">
          <p class="text-3xl font-bold text-primary">{$monitoringRuns.length}</p>
          <p class="text-sm text-base-content/60">Monitoring Runs</p>
        </div>
        
        <div class="text-center">
          <p class="text-3xl font-bold text-secondary">{$allArticles.length}</p>
          <p class="text-sm text-base-content/60">Articles Classified</p>
        </div>
        
        <div class="text-center">
          <p class="text-3xl font-bold text-accent">{$topicDistribution.length}</p>
          <p class="text-sm text-base-content/60">Active Topics</p>
        </div>
        
        <div class="text-center">
          <p class="text-3xl font-bold text-success">
            {calculateAvgClassificationRate().toFixed(1)}%
          </p>
          <p class="text-sm text-base-content/60">Classification Rate</p>
        </div>
      </div>
    </div>
  {/if}
</div>