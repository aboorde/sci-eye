<script>
  import { Calendar, ExternalLink } from 'lucide-svelte';
  import { allArticles } from '$lib/stores/articles';
  import { formatRelativeTime, truncateText, getTopicColor, stripHtmlTags, formatPublishedDate } from '$lib/utils/formatters';
  import { base } from '$app/paths';
  
  $: recentArticles = $allArticles
    .sort((a, b) => {
      const dateA = new Date(a.date_published || a.date_processed);
      const dateB = new Date(b.date_published || b.date_processed);
      return dateB - dateA;
    })
    .slice(0, 5);
</script>

<div class="glass-card rounded-xl p-6">
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-lg font-semibold">Recent Articles</h2>
    <a href="{base}/articles" class="btn btn-ghost btn-sm">
      View All
    </a>
  </div>
  
  {#if recentArticles.length === 0}
    <div class="text-center py-8 text-base-content/50">
      No articles available
    </div>
  {:else}
    <div class="space-y-4">
      {#each recentArticles as article}
        <div class="border-l-4 border-primary pl-4 py-2">
          <h3 class="font-medium mb-1 line-clamp-2">
            {stripHtmlTags(article.title)}
          </h3>
          
          <p class="text-sm text-base-content/60 mb-2 line-clamp-2">
            {truncateText(article.original_description, 120)}
          </p>
          
          <div class="flex flex-wrap items-center gap-2 text-xs">
            <div class="flex items-center gap-1 text-base-content/50">
              <Calendar size={12} />
              {formatPublishedDate(article.date_published)}
            </div>
            
            {#each article.topics.slice(0, 2) as topic}
              <span class="topic-badge {getTopicColor(topic)}">
                {topic}
              </span>
            {/each}
            
            {#if article.topics.length > 2}
              <span class="text-base-content/50">
                +{article.topics.length - 2} more
              </span>
            {/if}
            
            <a 
              href={article.link} 
              target="_blank" 
              rel="noopener noreferrer"
              class="ml-auto text-primary hover:text-primary-focus"
            >
              <ExternalLink size={14} />
            </a>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>