<script>
  import { Menu, Moon, Sun, RefreshCw, Download } from 'lucide-svelte';
  import { sidebarOpen, theme, toasts } from '$lib/stores/ui';
  import { monitoringRuns, isLoading } from '$lib/stores/articles';
  
  let isRefreshing = false;
  
  async function handleRefresh() {
    isRefreshing = true;
    toasts.show('Refreshing data...', 'info');
    
    // Reload the page to fetch new data
    window.location.reload();
  }
  
  function handleExport() {
    const data = $monitoringRuns;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pharma-news-export-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toasts.show('Data exported successfully', 'success');
  }
</script>

<header class="navbar bg-base-100 border-b border-base-200 px-4 lg:px-8">
  <div class="navbar-start">
    <button 
      class="btn btn-ghost btn-circle lg:hidden"
      on:click={() => sidebarOpen.update(n => !n)}
    >
      <Menu size={20} />
    </button>
    
    <div class="flex items-center gap-2">
      <div class="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
        <span class="text-white font-bold text-lg">P</span>
      </div>
      <div>
        <h1 class="text-xl font-bold gradient-text">Pharma News Monitor</h1>
        <p class="text-xs text-base-content/60">Real-time pharmaceutical intelligence</p>
      </div>
    </div>
  </div>

  <div class="navbar-end gap-2">
    <button 
      class="btn btn-ghost btn-sm gap-2"
      on:click={handleRefresh}
      disabled={isRefreshing || $isLoading}
    >
      <RefreshCw size={16} class={isRefreshing ? 'animate-spin' : ''} />
      <span class="hidden sm:inline">Refresh</span>
    </button>
    
    <button 
      class="btn btn-ghost btn-sm gap-2"
      on:click={handleExport}
      disabled={$isLoading || $monitoringRuns.length === 0}
    >
      <Download size={16} />
      <span class="hidden sm:inline">Export</span>
    </button>
    
    <button 
      class="btn btn-ghost btn-circle btn-sm"
      on:click={theme.toggle}
      aria-label="Toggle dark mode"
    >
      {#if $theme === 'pharmalight'}
        <Moon size={16} />
      {:else}
        <Sun size={16} />
      {/if}
    </button>
  </div>
</header>