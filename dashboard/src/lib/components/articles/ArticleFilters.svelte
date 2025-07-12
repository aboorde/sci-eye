<script>
  import { X } from 'lucide-svelte';
  import { filters, allArticles } from '$lib/stores/articles';
  import { getUniqueTopics, getUniqueSources } from '$lib/utils/dataLoader';
  
  let selectedTopics = [];
  let selectedSources = [];
  let minConfidence = null;
  
  $: availableTopics = getUniqueTopics($allArticles);
  $: availableSources = getUniqueSources($allArticles);
  
  $: filters.setTopics(selectedTopics);
  $: filters.setSources(selectedSources);
  $: filters.setMinConfidence(minConfidence);
  
  function toggleTopic(topic) {
    if (selectedTopics.includes(topic)) {
      selectedTopics = selectedTopics.filter(t => t !== topic);
    } else {
      selectedTopics = [...selectedTopics, topic];
    }
  }
  
  function toggleSource(source) {
    if (selectedSources.includes(source)) {
      selectedSources = selectedSources.filter(s => s !== source);
    } else {
      selectedSources = [...selectedSources, source];
    }
  }
  
  function clearAllFilters() {
    selectedTopics = [];
    selectedSources = [];
    minConfidence = null;
    filters.reset();
  }
</script>

<div class="glass-card rounded-lg p-6 space-y-6">
  <div class="flex items-center justify-between">
    <h3 class="text-lg font-semibold">Filters</h3>
    <button 
      class="btn btn-ghost btn-sm"
      on:click={clearAllFilters}
      disabled={selectedTopics.length === 0 && selectedSources.length === 0 && !minConfidence}
    >
      Clear All
    </button>
  </div>
  
  <!-- Topics Filter -->
  <div>
    <h4 class="font-medium mb-3">Topics</h4>
    <div class="flex flex-wrap gap-2">
      {#each availableTopics as topic}
        <button
          class="btn btn-xs"
          class:btn-primary={selectedTopics.includes(topic)}
          class:btn-ghost={!selectedTopics.includes(topic)}
          on:click={() => toggleTopic(topic)}
        >
          {topic}
        </button>
      {/each}
    </div>
  </div>
  
  <!-- Sources Filter -->
  <div>
    <h4 class="font-medium mb-3">Sources</h4>
    <div class="flex flex-wrap gap-2">
      {#each availableSources as source}
        <button
          class="btn btn-xs"
          class:btn-secondary={selectedSources.includes(source)}
          class:btn-ghost={!selectedSources.includes(source)}
          on:click={() => toggleSource(source)}
        >
          {source}
        </button>
      {/each}
    </div>
  </div>
  
  <!-- Confidence Filter -->
  <div>
    <h4 class="font-medium mb-3">Minimum Confidence</h4>
    <div class="flex items-center gap-4">
      <input 
        type="range"
        min="0"
        max="1"
        step="0.1"
        class="range range-primary flex-1"
        bind:value={minConfidence}
      />
      <span class="text-sm font-medium w-12">
        {minConfidence ? `${(minConfidence * 100).toFixed(0)}%` : 'Any'}
      </span>
    </div>
  </div>
  
  <!-- Active Filters Summary -->
  {#if selectedTopics.length > 0 || selectedSources.length > 0}
    <div class="border-t border-base-200 pt-4">
      <h4 class="text-sm font-medium mb-2">Active Filters:</h4>
      <div class="flex flex-wrap gap-2">
        {#each selectedTopics as topic}
          <div class="badge badge-primary gap-1">
            {topic}
            <button on:click={() => toggleTopic(topic)}>
              <X size={12} />
            </button>
          </div>
        {/each}
        {#each selectedSources as source}
          <div class="badge badge-secondary gap-1">
            {source}
            <button on:click={() => toggleSource(source)}>
              <X size={12} />
            </button>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>