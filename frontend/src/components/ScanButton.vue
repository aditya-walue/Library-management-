<template>
  <Button :size="size" :aria-label="label || 'Scan barcode or QR code'" :title="label || 'Scan barcode or QR code'" @click="open = true">
    <template #prefix><ScanLine class="size-4" /></template>
    <span v-if="label">{{ label }}</span>
  </Button>
  <ScanDialog v-model="open" @found="(article) => emit('found', article)" />
</template>

<script setup>
import { ref } from "vue"
import { ScanLine } from "lucide-vue-next"
import ScanDialog from "@/components/ScanDialog.vue"

defineProps({ label: String, size: { type: String, default: "sm" } })
const emit = defineEmits(["found"])
const open = ref(false)
</script>
