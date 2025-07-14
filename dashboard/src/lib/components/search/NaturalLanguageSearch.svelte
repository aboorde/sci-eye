<script>
  import { Search, Sparkles, ChevronRight, Brain } from 'lucide-svelte';
  import { createEventDispatcher } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  
  const dispatch = createEventDispatcher();
  
  let query = '';
  let isProcessing = false;
  let suggestions = [];
  let showExamples = false;
  
  const exampleQueries = [
    "Which companies announced positive Phase 3 results in oncology this month?",
    "Show me all FDA approvals for rare diseases",
    "What are the latest developments in CAR-T therapy?",
    "Find articles about Pfizer's COVID-19 developments",
    "Compare Novartis and Roche pipeline updates"
  ];
  
  async function handleSearch() {
    if (!query.trim() || isProcessing) return;
    
    isProcessing = true;
    
    try {
      // This would call your NLP API endpoint
      const response = await fetch('/api/search/natural-language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query,
          includeContext: true,
          limit: 20 
        })
      });
      
      const results = await response.json();
      dispatch('search', { query, results });
      
      // Store successful queries for suggestions
      addToSearchHistory(query);
      
    } catch (error) {
      console.error('Search failed:', error);
      dispatch('error', { message: 'Search failed. Please try again.' });
    } finally {
      isProcessing = false;
    }
  }
  
  function addToSearchHistory(searchQuery) {
    const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
    history.unshift(searchQuery);
    localStorage.setItem('searchHistory', JSON.stringify(history.slice(0, 10)));
  }
  
  function selectExample(example) {
    query = example;
    showExamples = false;
    handleSearch();
  }
  
  // Smart suggestions based on partial input
  $: if (query.length > 3) {
    generateSuggestions(query);
  } else {
    suggestions = [];
  }
  
  async function generateSuggestions(input) {
    // In production, this would call an API
    // For now, simple pattern matching
    const patterns = [
      { trigger: 'phase', suggestions: ['Phase 3 results', 'Phase 2 trials', 'Phase 1 safety'] },
      { trigger: 'fda', suggestions: ['FDA approval', 'FDA rejection', 'FDA accelerated approval'] },
      { trigger: 'company', suggestions: ['company merger', 'company pipeline', 'company earnings'] }
    ];
    
    const matches = patterns.filter(p => input.toLowerCase().includes(p.trigger));
    suggestions = matches.flatMap(m => m.suggestions);
  }
</script>

<div class="relative w-full max-w-4xl mx-auto">
  <!-- Main Search Input -->
  <div class="relative">
    <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
      {#if isProcessing}
        <div class="loading loading-spinner loading-sm text-primary"></div>
      {:else}
        <Brain size={20} class="text-primary" />
      {/if}
    </div>
    
    <input
      type="text"
      bind:value={query}
      on:keydown={(e) => e.key === 'Enter' && handleSearch()}
      placeholder="Ask anything about pharmaceutical news..."
      class="input input-bordered input-lg w-full pl-12 pr-32 
             focus:input-primary focus:shadow-lg transition-all duration-200"
      disabled={isProcessing}
    />
    
    <div class="absolute inset-y-0 right-0 flex items-center pr-2 gap-2">
      <button
        class="btn btn-ghost btn-sm"
        class:hidden={!query}
        on:click={() => query = ''}
      >
        Clear
      </button>
      
      <button
        class="btn btn-primary btn-sm gap-2"
        on:click={handleSearch}
        disabled={!query.trim() || isProcessing}
      >
        <Sparkles size={16} />
        Search
      </button>
    </div>
  </div>
  
  <!-- Smart Suggestions -->
  {#if suggestions.length > 0}
    <div 
      class="absolute z-10 w-full mt-2 bg-base-100 rounded-lg shadow-xl border border-base-300"
      transition:fly={{ y: -10, duration: 200 }}
    >
      <div class="p-2">
        <p class="text-xs text-base-content/50 px-2 mb-1">Suggestions</p>
        {#each suggestions as suggestion}
          <button
            class="w-full text-left px-3 py-2 rounded hover:bg-base-200 
                   text-sm flex items-center justify-between group"
            on:click={() => query = `${query} ${suggestion}`}
          >
            <span>{query} <strong>{suggestion}</strong></span>
            <ChevronRight size={14} class="opacity-0 group-hover:opacity-100 transition-opacity" />
          </button>
        {/each}
      </div>
    </div>
  {/if}
  
  <!-- Example Queries -->
  <div class="mt-4">
    <button
      class="text-sm text-base-content/60 hover:text-primary transition-colors"
      on:click={() => showExamples = !showExamples}
    >
      {showExamples ? 'Hide' : 'Show'} example queries
    </button>
    
    {#if showExamples}
      <div 
        class="mt-3 p-4 bg-base-200/50 rounded-lg"
        transition:fade={{ duration: 200 }}
      >
        <p class="text-sm font-medium mb-3">Try these natural language queries:</p>
        <div class="space-y-2">
          {#each exampleQueries as example}
            <button
              class="text-sm text-left w-full p-2 rounded hover:bg-base-300/50 
                     transition-colors flex items-center gap-2 group"
              on:click={() => selectExample(example)}
            >
              <Search size={14} class="text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
              <span>{example}</span>
            </button>
          {/each}
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Query Understanding Display -->
  {#if query && !isProcessing}
    <div class="mt-4 text-xs text-base-content/50">
      <span class="inline-flex items-center gap-1">
        <Sparkles size={12} />
        AI will understand: topics, companies, time ranges, and relationships
      </span>
    </div>
  {/if}
</div>

<style>
  input:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(var(--p), 0.1);
  }
  
  .animate-pulse-slow {
    animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
</style>