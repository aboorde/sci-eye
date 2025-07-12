<script>
  import { Search, X } from 'lucide-svelte';
  import { filters } from '$lib/stores/articles';
  
  let searchQuery = '';
  let inputEl;
  
  $: filters.setSearchQuery(searchQuery);
  
  function clearSearch() {
    searchQuery = '';
    inputEl.focus();
  }
</script>

<div class="relative">
  <Search 
    size={20} 
    class="absolute left-3 top-1/2 -translate-y-1/2 text-base-content/50 pointer-events-none" 
  />
  
  <input
    bind:this={inputEl}
    type="text"
    placeholder="Search articles by title, summary, or description..."
    class="input input-bordered w-full pl-10 pr-10"
    bind:value={searchQuery}
  />
  
  {#if searchQuery}
    <button
      class="absolute right-2 top-1/2 -translate-y-1/2 btn btn-ghost btn-xs btn-circle"
      on:click={clearSearch}
    >
      <X size={14} />
    </button>
  {/if}
</div>