<script>
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import { allArticles } from '$lib/stores/articles';
  import { calculateAverageConfidence } from '$lib/utils/dataProcessor';
  import { createBarChartConfig } from '$lib/utils/chartHelpers';
  
  Chart.register(...registerables);
  
  let canvas;
  let chart;
  
  $: confidenceData = calculateAverageConfidence($allArticles);
  $: if (chart && confidenceData.length > 0) {
    updateChart();
  }
  
  function updateChart() {
    const topConfidence = confidenceData.slice(0, 10);
    const labels = topConfidence.map(c => c.topic);
    const data = topConfidence.map(c => c.averageConfidence * 100);
    
    const config = createBarChartConfig(labels, [{
      label: 'Average Confidence %',
      data
    }], {
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: (value) => value + '%'
          }
        }
      }
    });
    
    if (chart) {
      chart.data = config.data;
      chart.options = config.options;
      chart.update();
    } else {
      chart = new Chart(canvas, config);
    }
  }
  
  onMount(() => {
    if (confidenceData.length > 0) {
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
  <h2 class="text-lg font-semibold mb-4">Classification Confidence by Topic</h2>
  
  {#if confidenceData.length === 0}
    <div class="flex items-center justify-center h-64 text-base-content/50">
      No confidence data available
    </div>
  {:else}
    <div class="chart-container" style="height: 350px;">
      <canvas bind:this={canvas} />
    </div>
  {/if}
</div>