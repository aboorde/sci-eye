<script>
  import { fade, fly } from 'svelte/transition';
  import { X, ExternalLink, Calendar, Clock, FileText, BarChart2 } from 'lucide-svelte';
  import { selectedArticle } from '$lib/stores/ui';
  import { 
    formatDate, 
    formatRelativeTime, 
    getTopicColor, 
    formatConfidence,
    getConfidenceColor 
  } from '$lib/utils/formatters';
  
  function closeModal() {
    selectedArticle.set(null);
  }
  
  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) {
      closeModal();
    }
  }
</script>

{#if $selectedArticle}
  <div 
    class="fixed inset-0 z-50 overflow-y-auto"
    transition:fade={{ duration: 200 }}
    on:click={handleBackdropClick}
  >
    <div class="flex items-center justify-center min-h-screen p-4">
      <div class="fixed inset-0 bg-black/50" />
      
      <div 
        class="relative bg-base-100 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
        transition:fly={{ y: 50, duration: 300 }}
      >
        <!-- Header -->
        <div class="sticky top-0 bg-base-100 border-b border-base-200 p-6 z-10">
          <div class="flex items-start justify-between gap-4">
            <h2 class="text-2xl font-bold pr-8">
              {$selectedArticle.title}
            </h2>
            <button 
              class="btn btn-ghost btn-circle btn-sm"
              on:click={closeModal}
            >
              <X size={20} />
            </button>
          </div>
        </div>
        
        <!-- Content -->
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-8rem)]">
          <!-- Metadata -->
          <div class="flex flex-wrap gap-4 mb-6 text-sm">
            <div class="flex items-center gap-2 text-base-content/60">
              <Calendar size={16} />
              {formatDate($selectedArticle.date_published, 'PPP')}
            </div>
            <div class="flex items-center gap-2 text-base-content/60">
              <Clock size={16} />
              Processed {formatRelativeTime($selectedArticle.date_processed)}
            </div>
            <div class="flex items-center gap-2 text-base-content/60">
              <FileText size={16} />
              {$selectedArticle.source_feed}
            </div>
            {#if $selectedArticle.has_full_content}
              <div class="badge badge-success badge-sm">Full content available</div>
            {/if}
          </div>
          
          <!-- Topics -->
          <div class="mb-6">
            <h3 class="font-semibold mb-3">Topics</h3>
            <div class="flex flex-wrap gap-2">
              {#each $selectedArticle.topics as topic}
                <div class="topic-badge {getTopicColor(topic)}">
                  <span>{topic}</span>
                  <span class="ml-2 {getConfidenceColor($selectedArticle.confidence_scores[topic])}">
                    {formatConfidence($selectedArticle.confidence_scores[topic])}
                  </span>
                </div>
              {/each}
            </div>
          </div>
          
          <!-- Summary -->
          <div class="mb-6">
            <h3 class="font-semibold mb-3">AI Summary</h3>
            <div class="prose prose-sm max-w-none">
              <p class="whitespace-pre-wrap text-base-content/80">
                {$selectedArticle.summary}
              </p>
            </div>
          </div>
          
          <!-- Original Description -->
          <div class="mb-6">
            <h3 class="font-semibold mb-3">Original Description</h3>
            <div class="bg-base-200/50 rounded-lg p-4">
              <p class="text-sm text-base-content/70">
                {$selectedArticle.original_description}
              </p>
            </div>
          </div>
          
          <!-- Confidence Scores -->
          <div class="mb-6">
            <h3 class="font-semibold mb-3">Classification Confidence</h3>
            <div class="space-y-2">
              {#each Object.entries($selectedArticle.confidence_scores) as [topic, score]}
                <div class="flex items-center gap-3">
                  <span class="text-sm w-48">{topic}</span>
                  <div class="flex-1 bg-base-200 rounded-full h-2 overflow-hidden">
                    <div 
                      class="h-full bg-primary transition-all duration-500"
                      style="width: {score * 100}%"
                    />
                  </div>
                  <span class="text-sm font-medium w-12 text-right {getConfidenceColor(score)}">
                    {formatConfidence(score)}
                  </span>
                </div>
              {/each}
            </div>
          </div>
          
          <!-- Actions -->
          <div class="flex gap-3 pt-4 border-t border-base-200">
            <a 
              href={$selectedArticle.link}
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn-primary gap-2"
            >
              <ExternalLink size={16} />
              Read Full Article
            </a>
            <button 
              class="btn btn-ghost"
              on:click={closeModal}
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}