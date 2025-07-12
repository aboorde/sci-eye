<script>
  import { TrendingUp, TrendingDown, Minus } from 'lucide-svelte';
  import { fly } from 'svelte/transition';
  
  export let title = '';
  export let value = '';
  export let subtitle = '';
  export let icon = null;
  export let trend = null; // { value: number, isPositive: boolean }
  export let delay = 0;
</script>

<div 
  class="metric-card"
  in:fly={{ y: 20, duration: 500, delay }}
>
  <div class="flex items-start justify-between mb-4">
    <div class="p-3 rounded-lg bg-primary/10">
      {#if icon}
        <svelte:component this={icon} size={24} class="text-primary" />
      {:else}
        <div class="w-6 h-6 bg-primary/20 rounded" />
      {/if}
    </div>
    
    {#if trend}
      <div class="flex items-center gap-1 text-sm">
        {#if trend.isPositive}
          <TrendingUp size={16} class="text-success" />
          <span class="text-success font-medium">+{trend.value}%</span>
        {:else if trend.value < 0}
          <TrendingDown size={16} class="text-error" />
          <span class="text-error font-medium">{trend.value}%</span>
        {:else}
          <Minus size={16} class="text-base-content/50" />
          <span class="text-base-content/50 font-medium">0%</span>
        {/if}
      </div>
    {/if}
  </div>
  
  <h3 class="text-sm font-medium text-base-content/60 mb-1">{title}</h3>
  <p class="text-2xl font-bold mb-1">{value}</p>
  
  {#if subtitle}
    <p class="text-xs text-base-content/50">{subtitle}</p>
  {/if}
</div>