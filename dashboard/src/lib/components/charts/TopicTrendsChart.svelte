<script>
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import { allArticles, chartTimeRange } from '$lib/stores/articles';
  import { groupArticlesByDate } from '$lib/utils/dataProcessor';
  import { createLineChartConfig } from '$lib/utils/chartHelpers';
  
  Chart.register(...registerables);
  
  let canvas;
  let chart;
  
  $: topicData = processTopicTrends($allArticles, $chartTimeRange);
  $: if (chart && topicData) {
    updateChart();
  }
  
  function processTopicTrends(articles, range) {
    // Group articles by date
    const grouped = groupArticlesByDate(articles);
    
    // Get top topics
    const topicCounts = {};
    articles.forEach(article => {
      article.topics.forEach(topic => {
        topicCounts[topic] = (topicCounts[topic] || 0) + 1;
      });
    });
    
    const topTopics = Object.entries(topicCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([topic]) => topic);
    
    // Build daily counts for each top topic
    const dates = Object.keys(grouped).sort();
    const datasets = topTopics.map(topic => {
      const data = dates.map(date => {
        const dayArticles = grouped[date] || [];
        return dayArticles.filter(a => a.topics.includes(topic)).length;
      });
      
      return {
        label: topic,
        data
      };
    });
    
    return { dates, datasets };
  }
  
  function updateChart() {
    if (!topicData) return;
    
    const config = createLineChartConfig(topicData.dates, topicData.datasets, {
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
    if (topicData) {
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
  <h2 class="text-lg font-semibold mb-4">Topic Trends Over Time</h2>
  
  {#if !topicData || topicData.datasets.length === 0}
    <div class="flex items-center justify-center h-64 text-base-content/50">
      No topic trend data available
    </div>
  {:else}
    <div class="chart-container" style="height: 300px;">
      <canvas bind:this={canvas} />
    </div>
  {/if}
</div>