<template>
  <div class="flex flex-col items-center px-6 py-12 text-center">
    <span class="flex size-10 items-center justify-center rounded-full bg-paper text-ink-muted">
      <component :is="icon" class="size-5" :stroke-width="1.75" />
    </span>
    <p class="mt-3 font-medium text-ink">{{ title }}</p>
    <p v-if="text" class="mt-1 max-w-xs text-sm text-ink-muted">{{ text }}</p>
    <div v-if="$slots.default" class="mt-4"><slot /></div>
  </div>
</template>

<script setup>
defineProps({ icon: [Object, Function], title: String, text: String })
</script>
