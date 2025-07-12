<script>
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import { sourceDistribution } from '$lib/stores/articles';
  import { createBarChartConfig } from '$lib/utils/chartHelpers';
  
  Chart.register(...registerables);
  
  let canvas;
  let chart;
  
  $: if (chart && $sourceDistribution.length > 0) {
    updateChart();
  }
  
  function updateChart() {
    const labels = $sourceDistribution.map(s => s.source);
    const data = $sourceDistribution.map(s => s.count);
    
    const config = createBarChartConfig(labels, [{
      label: 'Articles',
      data
    }], {
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
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
    if ($sourceDistribution.length > 0) {
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
  <h2 class="text-lg font-semibold mb-4">Source Distribution</h2>
  
  {#if $sourceDistribution.length === 0}
    <div class="flex items-center justify-center h-64 text-base-content/50">
      No source data available
    </div>
  {:else}
    <div class="chart-container" style="height: 300px;">
      <canvas bind:this={canvas} />
    </div>
  {/if}
</div>