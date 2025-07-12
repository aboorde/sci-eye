<script>
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import { dailyMetrics, chartTimeRange } from '$lib/stores/articles';
  import { createLineChartConfig } from '$lib/utils/chartHelpers';
  
  Chart.register(...registerables);
  
  let canvas;
  let chart;
  
  $: filteredMetrics = filterByTimeRange($dailyMetrics, $chartTimeRange);
  $: if (chart && filteredMetrics.length > 0) {
    updateChart();
  }
  
  function filterByTimeRange(metrics, range) {
    if (range === 'all') return metrics;
    
    const days = {
      '7d': 7,
      '30d': 30,
      '90d': 90
    }[range] || 7;
    
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    
    return metrics.filter(m => new Date(m.date) >= cutoff);
  }
  
  function updateChart() {
    const labels = filteredMetrics.map(m => m.date);
    const datasets = [
      {
        label: 'Articles Fetched',
        data: filteredMetrics.map(m => m.totalFetched)
      },
      {
        label: 'Articles Classified',
        data: filteredMetrics.map(m => m.totalClassified)
      }
    ];
    
    const config = createLineChartConfig(labels, datasets, {
      plugins: {
        title: {
          display: false
        }
      }
    });
    
    if (chart) {
      chart.data = config.data;
      chart.update();
    } else {
      chart = new Chart(canvas, config);
    }
  }
  
  onMount(() => {
    if (filteredMetrics.length > 0) {
      updateChart();
    }
  });
  
  onDestroy(() => {
    if (chart) {
      chart.destroy();
    }
  });
</script>

<div class="glass-card rounded-xl p-6">
  <h2 class="text-lg font-semibold mb-4">Daily Activity Trends</h2>
  
  {#if filteredMetrics.length === 0}
    <div class="flex items-center justify-center h-64 text-base-content/50">
      No data available for selected time range
    </div>
  {:else}
    <div class="chart-container" style="height: 300px;">
      <canvas bind:this={canvas} />
    </div>
  {/if}
</div>