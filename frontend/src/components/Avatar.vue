<template>
  <span
    class="inline-flex shrink-0 items-center justify-center rounded-full font-semibold"
    :class="size === 'lg' ? 'size-12 text-base' : size === 'sm' ? 'size-7 text-[11px]' : 'size-8 text-xs'"
    :style="{ backgroundColor: tint.bg, color: tint.fg }"
    aria-hidden="true"
  >
    {{ initials(name) }}
  </span>
</template>

<script setup>
import { computed } from "vue"
import { hash, initials } from "@/utils"

const props = defineProps({ name: String, seed: String, size: String })

const tints = [
  { bg: "#0F9F6E1F", fg: "#0B7F58" },
  { bg: "#2F6FE41F", fg: "#2F6FE4" },
  { bg: "#D9485F1F", fg: "#C23A50" },
  { bg: "#E07A2E1F", fg: "#C2651F" },
  { bg: "#7C5CE01F", fg: "#6A4AD0" },
  { bg: "#0E9AA71F", fg: "#0B8591" },
]
const tint = computed(() => tints[Math.floor(hash(props.seed || props.name) * tints.length)])
</script>
