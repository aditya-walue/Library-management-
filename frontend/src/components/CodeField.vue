<template>
  <div>
    <label class="mb-1.5 block text-xs text-ink-gray-5" :for="id">{{ label }}</label>
    <div class="flex gap-2">
      <TextInput :id="id" v-model="value" :placeholder="placeholder" class="flex-1" />
      <ScanButton kind="code" size="md" :label="undefined" @found="(code) => (value = code)" />
    </div>
  </div>
</template>

<script setup>
import { TextInput } from "frappe-ui"
import ScanButton from "@/components/ScanButton.vue"

defineProps({ label: String, placeholder: String })
const value = defineModel({ type: String })
const id = `code-${Math.random().toString(36).slice(2, 8)}`
</script>
