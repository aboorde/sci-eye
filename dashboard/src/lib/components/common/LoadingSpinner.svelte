<script>
  export let size = 'md';
  
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };
</script>

<div class="flex items-center justify-center p-8">
  <div class="relative {sizes[size]}">
    <div class="absolute inset-0 bg-primary/20 rounded-full animate-ping" />
    <div class="relative {sizes[size]} border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
  </div>
</div>