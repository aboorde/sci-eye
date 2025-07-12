<script>
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import ChartDataLabels from 'chartjs-plugin-datalabels';
  import { topicDistribution } from '$lib/stores/articles';
  import { createPieChartConfig } from '$lib/utils/chartHelpers';
  
  Chart.register(...registerables, ChartDataLabels);
  
  let canvas;
  let chart;
  
  $: if (chart && $topicDistribution.length > 0) {
    updateChart();
  }
  
  function updateChart() {
    const topTopics = $topicDistribution.slice(0, 8);
    const labels = topTopics.map(t => t.topic);
    const data = topTopics.map(t => t.count);
    
    const config = createPieChartConfig(labels, data, {
      plugins: {
        title: {
          display: false
        },
        legend: {
          position: 'right',
          labels: {
            padding: 12,
            font: {
              size: 11
            }
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
    if ($topicDistribution.length > 0) {
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
  <h2 class="text-lg font-semibold mb-4">Topic Distribution</h2>
  
  {#if $topicDistribution.length === 0}
    <div class="flex items-center justify-center h-64 text-base-content/50">
      No topic data available
    </div>
  {:else}
    <div class="chart-container" style="height: 300px;">
      <canvas bind:this={canvas} />
    </div>
  {/if}
</div>