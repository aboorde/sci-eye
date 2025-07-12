<script>
  import { fly } from 'svelte/transition';
  import { Check, X, Info, AlertTriangle } from 'lucide-svelte';
  import { toasts } from '$lib/stores/ui';
  
  const icons = {
    success: Check,
    error: X,
    info: Info,
    warning: AlertTriangle
  };
  
  const colors = {
    success: 'alert-success',
    error: 'alert-error',
    info: 'alert-info',
    warning: 'alert-warning'
  };
</script>

<div class="fixed bottom-4 right-4 z-50 space-y-2">
  {#each $toasts as toast (toast.id)}
    <div 
      class="alert {colors[toast.type]} shadow-lg max-w-sm"
      transition:fly={{ y: 50, duration: 300 }}
    >
      <svelte:component this={icons[toast.type]} size={20} />
      <span>{toast.message}</span>
      <button 
        class="btn btn-ghost btn-xs btn-circle"
        on:click={() => toasts.dismiss(toast.id)}
      >
        <X size={14} />
      </button>
    </div>
  {/each}
</div>