<script>
  import { Activity, Zap, Clock, TrendingUp, Copy } from 'lucide-svelte';
  import { monitoringRuns } from '$lib/stores/articles';
  
  $: latestRun = $monitoringRuns[0] || null;
  $: performanceStats = calculatePerformanceStats();
  
  function calculatePerformanceStats() {
    if (!latestRun) return null;
    
    const fetched = latestRun.total_articles_fetched || 0;
    const duplicates = latestRun.total_duplicates_skipped || 0;
    const unique = latestRun.total_unique_articles || (fetched - duplicates);
    const classified = latestRun.total_articles_classified || 0;
    const discarded = latestRun.total_articles_discarded || 0;
    
    // Estimate time saved (3 seconds per discarded article + 5 seconds per duplicate)
    const timeSaved = (discarded * 3) + (duplicates * 5);
    
    return {
      classificationRate: unique > 0 ? (classified / unique * 100).toFixed(1) : 0,
      articlesSkipped: discarded,
      duplicatesSkipped: duplicates,
      timeSaved: formatTime(timeSaved),
      efficiency: fetched > 0 ? ((discarded + duplicates) / fetched * 100).toFixed(0) : 0
    };
  }
  
  function formatTime(seconds) {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  }
</script>

<div class="glass-card rounded-xl p-6">
  <h2 class="text-lg font-semibold mb-4">Performance Metrics</h2>
  
  {#if performanceStats}
    <div class="space-y-4">
      <div class="flex items-start gap-3">
        <div class="p-2 bg-primary/10 rounded-lg">
          <Zap size={16} class="text-primary" />
        </div>
        <div class="flex-1">
          <p class="text-sm font-medium">Classification Rate</p>
          <p class="text-2xl font-bold text-primary">{performanceStats.classificationRate}%</p>
        </div>
      </div>
      
      <div class="flex items-start gap-3">
        <div class="p-2 bg-success/10 rounded-lg">
          <Activity size={16} class="text-success" />
        </div>
        <div class="flex-1">
          <p class="text-sm font-medium">Articles Skipped</p>
          <p class="text-2xl font-bold text-success">{performanceStats.articlesSkipped}</p>
        </div>
      </div>
      
      <div class="flex items-start gap-3">
        <div class="p-2 bg-warning/10 rounded-lg">
          <Copy size={16} class="text-warning" />
        </div>
        <div class="flex-1">
          <p class="text-sm font-medium">Duplicates Removed</p>
          <p class="text-2xl font-bold text-warning">{performanceStats.duplicatesSkipped}</p>
        </div>
      </div>
      
      <div class="flex items-start gap-3">
        <div class="p-2 bg-accent/10 rounded-lg">
          <Clock size={16} class="text-accent" />
        </div>
        <div class="flex-1">
          <p class="text-sm font-medium">Time Saved</p>
          <p class="text-2xl font-bold text-accent">{performanceStats.timeSaved}</p>
        </div>
      </div>
      
      <div class="divider my-2" />
      
      <div class="bg-base-200/50 rounded-lg p-3">
        <div class="flex items-center gap-2 mb-1">
          <TrendingUp size={14} class="text-primary" />
          <p class="text-xs font-medium">Efficiency Score</p>
        </div>
        <p class="text-sm">
          <span class="font-bold text-primary">{performanceStats.efficiency}%</span>
          <span class="text-base-content/60"> of articles filtered early</span>
        </p>
      </div>
    </div>
  {:else}
    <div class="text-center py-8 text-base-content/50">
      No performance data available
    </div>
  {/if}
</div>