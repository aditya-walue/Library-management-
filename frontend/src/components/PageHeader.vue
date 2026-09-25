<template>
  <header class="flex flex-wrap items-end justify-between gap-4 pb-7 pt-10">
    <div class="min-w-0">
      <h1 class="font-display text-[2.1rem] font-medium leading-tight tracking-[-0.015em] text-ink">{{ title }}</h1>
      <p v-if="subtitle" class="mt-1 text-[15px] text-ink-muted">{{ subtitle }}</p>
    </div>
    <div class="flex items-center gap-2">
      <slot />
    </div>
  </header>
</template>

<script setup>
defineProps({ title: String, subtitle: String })
</script>
