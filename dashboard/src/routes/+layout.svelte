<script>
  import '../app.css';
  import { onMount } from 'svelte';
  import { initializeData } from '$lib/stores/articles';
  import { theme } from '$lib/stores/ui';
  import Header from '$lib/components/layout/Header.svelte';
  import Sidebar from '$lib/components/layout/Sidebar.svelte';
  import Toast from '$lib/components/common/Toast.svelte';
  
  onMount(() => {
    theme.init();
    initializeData();
  });
</script>

<div class="min-h-screen bg-base-100">
  <Header />
  
  <div class="flex h-[calc(100vh-4rem)]">
    <Sidebar />
    
    <main class="flex-1 overflow-y-auto">
      <div class="container mx-auto p-4 lg:p-8">
        <slot />
      </div>
    </main>
  </div>
</div>

<Toast />