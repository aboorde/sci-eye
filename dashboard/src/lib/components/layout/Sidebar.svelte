<script>
  import { page } from '$app/stores';
  import { base } from '$app/paths';
  import { 
    LayoutDashboard, 
    FileText, 
    BarChart3, 
    Brain,
    Filter,
    X
  } from 'lucide-svelte';
  import { sidebarOpen } from '$lib/stores/ui';
  import { allArticles, topicDistribution } from '$lib/stores/articles';
  
  const menuItems = [
    { 
      icon: LayoutDashboard, 
      label: 'Dashboard', 
      href: `${base}/`,
      badge: null
    },
    { 
      icon: FileText, 
      label: 'Articles', 
      href: `${base}/articles`,
      badge: $allArticles.length
    },
    { 
      icon: BarChart3, 
      label: 'Analytics', 
      href: `${base}/analytics`,
      badge: null
    },
    { 
      icon: Brain, 
      label: 'Insights', 
      href: `${base}/insights`,
      badge: $topicDistribution.length
    }
  ];
  
  $: isActive = (href) => {
    if (href === `${base}/` && $page.url.pathname === `${base}/`) return true;
    if (href !== `${base}/` && $page.url.pathname.startsWith(href)) return true;
    return false;
  };
</script>

<aside 
  class="fixed inset-y-0 left-0 z-20 w-64 bg-base-200 transform transition-transform duration-300 lg:translate-x-0 lg:static lg:inset-0"
  class:translate-x-0={$sidebarOpen}
  class:-translate-x-full={!$sidebarOpen}
>
  <div class="flex flex-col h-full">
    <div class="flex items-center justify-between p-4 lg:hidden">
      <h2 class="text-lg font-semibold">Menu</h2>
      <button 
        class="btn btn-ghost btn-sm btn-circle"
        on:click={() => sidebarOpen.set(false)}
      >
        <X size={16} />
      </button>
    </div>

    <nav class="flex-1 px-4 pb-4 space-y-2">
      {#each menuItems as item}
        <a 
          href={item.href}
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200"
          class:bg-primary={isActive(item.href)}
          class:text-primary-content={isActive(item.href)}
          class:hover:bg-base-300={!isActive(item.href)}
          on:click={() => window.innerWidth < 1024 && sidebarOpen.set(false)}
        >
          <svelte:component this={item.icon} size={20} />
          <span class="font-medium">{item.label}</span>
          {#if item.badge}
            <span class="ml-auto badge badge-sm" 
              class:badge-primary-content={isActive(item.href)}
              class:badge-neutral={!isActive(item.href)}
            >
              {item.badge}
            </span>
          {/if}
        </a>
      {/each}
    </nav>

    <div class="p-4 border-t border-base-300">
      <div class="bg-base-100 rounded-lg p-4">
        <h3 class="font-semibold text-sm mb-2">Quick Stats</h3>
        <div class="space-y-2 text-xs">
          <div class="flex justify-between">
            <span class="text-base-content/60">Total Articles</span>
            <span class="font-medium">{$allArticles.length}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-base-content/60">Topics Tracked</span>
            <span class="font-medium">{$topicDistribution.length}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</aside>

{#if $sidebarOpen}
  <div 
    class="fixed inset-0 bg-black/50 z-10 lg:hidden"
    on:click={() => sidebarOpen.set(false)}
  />
{/if}