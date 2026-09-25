<template>
  <div class="flex items-center gap-4 rounded-xl border border-paper-line p-3">
    <img v-if="src" :src="src" :alt="`Library card QR for ${member.full_name}`" class="size-20 rounded-md" />
    <div class="min-w-0 flex-1">
      <p class="text-sm font-medium text-ink">Library card</p>
      <p class="mt-0.5 text-xs text-ink-muted">
        For members without an ID card. Scanning it selects the member when issuing.
      </p>
      <Button size="sm" class="mt-2" @click="printCard">
        <template #prefix><Printer class="size-4" /></template>
        Print card
      </Button>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect } from "vue"
import QRCode from "qrcode"
import { Printer } from "lucide-vue-next"
import { memberQrValue } from "@/utils"

const props = defineProps({ member: { type: Object, required: true } })
const src = ref("")

watchEffect(async () => {
  src.value = await QRCode.toDataURL(memberQrValue(props.member.name), { margin: 1, width: 240 })
})

function printCard() {
  const esc = (s) => String(s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c])
  const m = props.member
  const w = window.open("", "_blank", "width=480,height=360")
  if (!w) return
  w.document.write(`<!doctype html><title>Library card</title>
    <style>
      @page { size: 85.6mm 54mm; margin: 0 }
      body { margin: 0; font: 11px/1.35 -apple-system, system-ui, sans-serif; color: #1a1d1b }
      .card { width: 85.6mm; height: 54mm; box-sizing: border-box; padding: 4mm; display: flex; flex-direction: column; border-top: 4mm solid #1F3A2E }
      .row { display: flex; gap: 4mm; align-items: center; flex: 1 }
      img { width: 26mm; height: 26mm }
      h1 { font: 600 14px/1.2 Georgia, serif; margin: 0 0 1mm }
      .muted { color: #5c625e }
      .brand { font: 600 10px/1 Georgia, serif; color: #1F3A2E }
    </style>
    <div class="card">
      <div class="brand">Library card</div>
      <div class="row">
        <img src="${src.value}" />
        <div>
          <h1>${esc(m.full_name)}</h1>
          <div class="muted">${esc(m.membership_type)} member</div>
          <div>${esc(m.card_id || m.user || m.name)}</div>
        </div>
      </div>
    </div>
    <script>window.onload = () => { window.print(); window.onafterprint = () => window.close() }<\/script>`)
  w.document.close()
}
</script>
