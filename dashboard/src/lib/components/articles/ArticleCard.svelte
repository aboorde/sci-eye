<script>
  import { Calendar, ExternalLink, BarChart2, Newspaper } from 'lucide-svelte';
  import { selectedArticle } from '$lib/stores/ui';
  import { 
    formatDate, 
    formatRelativeTime, 
    truncateText, 
    getTopicColor, 
    formatConfidence,
    getSourceIcon 
  } from '$lib/utils/formatters';
  
  export let article;
  export let viewMode = 'grid';
  
  function handleClick() {
    selectedArticle.set(article);
  }
  
  $: maxConfidence = Math.max(...Object.values(article.confidence_scores || {}));
</script>

<div 
  class="article-card cursor-pointer {viewMode === 'list' ? 'flex gap-4' : ''}"
  on:click={handleClick}
  on:keydown={(e) => e.key === 'Enter' && handleClick()}
  role="button"
  tabindex="0"
>
  {#if viewMode === 'grid'}
    <!-- Grid View -->
    <div class="flex items-start justify-between mb-3">
      <div class="p-2 bg-primary/10 rounded-lg">
        <svelte:component this={Newspaper} size={20} class="text-primary" />
      </div>
      <span class="text-xs text-base-content/50">
        {formatRelativeTime(article.date_processed)}
      </span>
    </div>
    
    <h3 class="font-semibold mb-2 line-clamp-2">
      {article.title}
    </h3>
    
    <p class="text-sm text-base-content/60 mb-3 line-clamp-3">
      {truncateText(article.summary || article.original_description, 150)}
    </p>
    
    <div class="flex flex-wrap gap-2 mb-3">
      {#each article.topics.slice(0, 3) as topic}
        <span class="topic-badge {getTopicColor(topic)} text-xs">
          {topic}
        </span>
      {/each}
      {#if article.topics.length > 3}
        <span class="text-xs text-base-content/50">+{article.topics.length - 3}</span>
      {/if}
    </div>
    
    <div class="flex items-center justify-between text-xs text-base-content/50">
      <span class="flex items-center gap-1">
        <BarChart2 size={12} />
        {formatConfidence(maxConfidence)}
      </span>
      <span>{article.source_feed}</span>
    </div>
  {:else}
    <!-- List View -->
    <div class="flex-1">
      <div class="flex items-start justify-between mb-2">
        <h3 class="font-semibold line-clamp-1 flex-1 mr-4">
          {article.title}
        </h3>
        <span class="text-xs text-base-content/50 whitespace-nowrap">
          {formatRelativeTime(article.date_processed)}
        </span>
      </div>
      
      <p class="text-sm text-base-content/60 mb-2 line-clamp-2">
        {truncateText(article.summary || article.original_description, 200)}
      </p>
      
      <div class="flex items-center gap-4 text-xs">
        <div class="flex flex-wrap gap-2">
          {#each article.topics.slice(0, 2) as topic}
            <span class="topic-badge {getTopicColor(topic)}">
              {topic}
            </span>
          {/each}
          {#if article.topics.length > 2}
            <span class="text-base-content/50">+{article.topics.length - 2}</span>
          {/if}
        </div>
        
        <span class="text-base-content/50">•</span>
        <span class="text-base-content/50">{article.source_feed}</span>
        <span class="text-base-content/50">•</span>
        <span class="text-base-content/50 flex items-center gap-1">
          <BarChart2 size={12} />
          {formatConfidence(maxConfidence)}
        </span>
      </div>
    </div>
  {/if}
  
  <a 
    href={article.link}
    target="_blank"
    rel="noopener noreferrer"
    class="btn btn-ghost btn-xs btn-circle ml-auto"
    on:click|stopPropagation
  >
    <ExternalLink size={14} />
  </a>
</div>