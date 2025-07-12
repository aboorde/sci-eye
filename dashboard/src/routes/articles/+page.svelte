<script>
  import { Grid3x3, List, Search, Filter } from 'lucide-svelte';
  import ArticleCard from '$lib/components/articles/ArticleCard.svelte';
  import ArticleDetail from '$lib/components/articles/ArticleDetail.svelte';
  import ArticleFilters from '$lib/components/articles/ArticleFilters.svelte';
  import SearchBar from '$lib/components/common/SearchBar.svelte';
  import LoadingSpinner from '$lib/components/common/LoadingSpinner.svelte';
  import { 
    filteredArticles, 
    isLoading,
    filters
  } from '$lib/stores/articles';
  import { articleViewMode } from '$lib/stores/ui';
  
  let showFilters = false;
</script>

<svelte:head>
  <title>Articles - Pharma News Monitor</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div>
    <h1 class="text-3xl font-bold mb-2">Articles</h1>
    <p class="text-base-content/60">
      Browse and search through {$filteredArticles.length} classified pharmaceutical news articles
    </p>
  </div>

  {#if $isLoading}
    <LoadingSpinner size="lg" />
  {:else}
    <!-- Controls -->
    <div class="flex flex-col sm:flex-row gap-4">
      <div class="flex-1">
        <SearchBar />
      </div>
      
      <div class="flex gap-2">
        <button 
          class="btn btn-ghost gap-2"
          class:btn-active={showFilters}
          on:click={() => showFilters = !showFilters}
        >
          <Filter size={16} />
          Filters
          {#if $filters.topics.length + $filters.sources.length > 0}
            <span class="badge badge-primary badge-sm">
              {$filters.topics.length + $filters.sources.length}
            </span>
          {/if}
        </button>
        
        <div class="btn-group">
          <button 
            class="btn btn-ghost btn-sm"
            class:btn-active={$articleViewMode === 'grid'}
            on:click={() => articleViewMode.set('grid')}
          >
            <Grid3x3 size={16} />
          </button>
          <button 
            class="btn btn-ghost btn-sm"
            class:btn-active={$articleViewMode === 'list'}
            on:click={() => articleViewMode.set('list')}
          >
            <List size={16} />
          </button>
        </div>
      </div>
    </div>
    
    <!-- Filters Panel -->
    {#if showFilters}
      <div class="animate-slide-up">
        <ArticleFilters />
      </div>
    {/if}
    
    <!-- Articles Grid/List -->
    {#if $filteredArticles.length === 0}
      <div class="text-center py-16">
        <p class="text-lg text-base-content/50">No articles match your filters</p>
        <button 
          class="btn btn-ghost btn-sm mt-4"
          on:click={() => filters.reset()}
        >
          Clear Filters
        </button>
      </div>
    {:else}
      <div 
        class="grid gap-4"
        class:grid-cols-1={$articleViewMode === 'list'}
        class:md:grid-cols-2={$articleViewMode === 'grid'}
        class:lg:grid-cols-3={$articleViewMode === 'grid'}
      >
        {#each $filteredArticles as article, i}
          <div 
            class="animate-fade-in"
            style="animation-delay: {i * 50}ms"
          >
            <ArticleCard {article} viewMode={$articleViewMode} />
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<!-- Article Detail Modal -->
<ArticleDetail />