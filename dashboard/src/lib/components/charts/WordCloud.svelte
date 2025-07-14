<script>
  import { allArticles } from '$lib/stores/articles';
  import { stripHtmlTags } from '$lib/utils/formatters';
  
  $: wordFrequencies = calculateWordFrequencies($allArticles);
  
  function calculateWordFrequencies(articles) {
    const stopWords = new Set([
      'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
      'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'been', 'be',
      'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
      'should', 'may', 'might', 'must', 'shall', 'can', 'this', 'that',
      'these', 'those', 'it', 'its', 'their', 'them', 'they', 'we', 'our'
    ]);
    
    const wordCounts = {};
    
    articles.forEach(article => {
      const text = `${stripHtmlTags(article.title)} ${article.summary || article.original_description}`.toLowerCase();
      const words = text.match(/\b[a-z]{4,}\b/g) || [];
      
      words.forEach(word => {
        if (!stopWords.has(word) && word.length > 4) {
          wordCounts[word] = (wordCounts[word] || 0) + 1;
        }
      });
    });
    
    return Object.entries(wordCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 40)
      .map(([word, count]) => ({ word, count }));
  }
  
  function getFontSize(count, maxCount) {
    const minSize = 0.8;
    const maxSize = 2.5;
    return minSize + (count / maxCount) * (maxSize - minSize);
  }
  
  function getOpacity(count, maxCount) {
    const minOpacity = 0.4;
    const maxOpacity = 1;
    return minOpacity + (count / maxCount) * (maxOpacity - minOpacity);
  }
</script>

<div class="glass-card rounded-xl p-6">
  <h2 class="text-lg font-semibold mb-4">Common Terms</h2>
  
  {#if wordFrequencies.length === 0}
    <div class="flex items-center justify-center h-64 text-base-content/50">
      No word data available
    </div>
  {:else}
    <div class="flex flex-wrap gap-2 items-center justify-center p-4">
      {#each wordFrequencies as { word, count }}
        <span 
          class="inline-block px-2 py-1 hover:text-primary transition-colors cursor-default"
          style="
            font-size: {getFontSize(count, wordFrequencies[0].count)}rem;
            opacity: {getOpacity(count, wordFrequencies[0].count)};
          "
          title="{word}: {count} occurrences"
        >
          {word}
        </span>
      {/each}
    </div>
  {/if}
</div>