<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium"
    :style="{ backgroundColor: tintFor(category, '14'), color: colorFor(category) }"
  >
    <span class="size-1.5 rounded-full" :style="{ backgroundColor: colorFor(category) }" />
    {{ category }}
  </span>
</template>

<script setup>
import { colorFor, tintFor } from "@/utils"

defineProps({ category: String })
</script>
