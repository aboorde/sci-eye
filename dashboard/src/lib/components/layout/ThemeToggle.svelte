<script>
  import { theme, isDarkMode } from '$lib/stores/theme';
  import { Sun, Moon } from 'lucide-svelte';
</script>

<button
  class="btn btn-circle btn-ghost swap swap-rotate"
  on:click={theme.toggle}
  aria-label="Toggle theme"
>
  {#if $isDarkMode}
    <Sun class="w-5 h-5" />
  {:else}
    <Moon class="w-5 h-5" />
  {/if}
</button>