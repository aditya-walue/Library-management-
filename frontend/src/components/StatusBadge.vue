<template>
  <span class="inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset" :class="tone">
    <span class="size-1.5 rounded-full bg-current" />
    {{ status }}
  </span>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({ status: String })

const tones = {
  green: "bg-[#0F9F6E]/10 text-[#0B7F58] ring-[#0F9F6E]/20",
  brick: "bg-[#D9485F]/10 text-[#C23A50] ring-[#D9485F]/20",
  ink: "bg-[#2F6FE4]/10 text-[#2F6FE4] ring-[#2F6FE4]/20",
  gray: "bg-paper text-ink-muted ring-ink/10",
}
const map = {
  Available: "green",
  Active: "green",
  Returned: "green",
  Issued: "ink",
  Overdue: "brick",
  Unavailable: "gray",
  Inactive: "gray",
}
const tone = computed(() => tones[map[props.status] || "gray"])
</script>
