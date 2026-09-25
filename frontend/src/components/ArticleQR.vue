<template>
  <div class="flex items-center gap-4 rounded-xl border border-paper-line p-3">
    <img v-if="src" :src="src" :alt="`QR code for ${article.title}`" class="size-24 rounded-md" />
    <div class="min-w-0 flex-1">
      <p class="text-sm font-medium text-ink">Shelf label</p>
      <p class="mt-0.5 text-xs text-ink-muted">
        Stick this on the book. Scanning it opens the title in the catalogue and fills it in when issuing.
      </p>
      <Button size="sm" class="mt-2" @click="printLabel">
        <template #prefix><Printer class="size-4" /></template>
        Print label
      </Button>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect } from "vue"
import QRCode from "qrcode"
import { Printer } from "lucide-vue-next"
import { articleQrValue } from "@/utils"

const props = defineProps({ article: { type: Object, required: true } })
const src = ref("")

watchEffect(async () => {
  src.value = await QRCode.toDataURL(articleQrValue(props.article.name), { margin: 1, width: 240 })
})

function printLabel() {
  const esc = (s) => String(s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c])
  const w = window.open("", "_blank", "width=420,height=520")
  if (!w) return
  w.document.write(`<!doctype html><title>Label</title>
    <style>
      @page { size: 60mm 40mm; margin: 0 }
      body { margin: 0; font: 11px/1.3 -apple-system, system-ui, sans-serif }
      .label { width: 60mm; height: 40mm; box-sizing: border-box; padding: 3mm; display: flex; gap: 3mm; align-items: center }
      img { width: 30mm; height: 30mm }
      b { display: block; font-size: 12px; margin-bottom: 1mm }
      small { color: #555 }
    </style>
    <div class="label">
      <img src="${src.value}" />
      <div><b>${esc(props.article.title)}</b>${esc(props.article.author)}<br /><small>${esc(props.article.isbn || props.article.name)}</small></div>
    </div>
    <script>window.onload = () => { window.print(); window.onafterprint = () => window.close() }<\/script>`)
  w.document.close()
}
</script>
