<template>
  <Dialog v-model="show" :options="{ title: 'Scan article', size: 'md' }">
    <template #body-content>
      <div class="space-y-4">
        <div class="relative aspect-[4/3] overflow-hidden rounded-xl bg-ink">
          <video v-show="cameraOn" ref="video" class="size-full object-cover" muted playsinline />
          <div v-if="cameraOn" class="pointer-events-none absolute inset-0 flex items-center justify-center">
            <div class="h-1/2 w-3/4 rounded-lg border-2 border-white/80 shadow-[0_0_0_9999px_rgba(0,0,0,0.35)]" />
          </div>
          <div v-else class="flex size-full flex-col items-center justify-center gap-2 px-6 text-center text-sm text-white/80">
            <CameraOff class="size-6" />
            <p>{{ cameraMessage }}</p>
          </div>
          <div
            v-if="resolving"
            class="absolute inset-0 flex items-center justify-center bg-ink/60 text-sm font-medium text-white"
          >
            Looking up {{ lastCode }}…
          </div>
        </div>

        <p class="text-center text-sm text-ink-muted">
          Point the camera at the book's ISBN barcode or its library QR label.
        </p>

        <ErrorMessage :message="error" />

        <div class="flex items-center gap-2">
          <TextInput
            v-model="manual"
            placeholder="Or type an ISBN or article code"
            class="flex-1"
            @keydown.enter="lookup(manual)"
          />
          <Button :disabled="!manual.trim()" @click="lookup(manual)">Find</Button>
        </div>
        <label class="flex cursor-pointer items-center justify-center gap-2 rounded-lg border border-dashed border-paper-line py-2.5 text-sm text-ink-muted hover:border-ink-faint hover:text-ink">
          <ImageUp class="size-4" />
          Scan from a photo
          <input type="file" accept="image/*" capture="environment" class="sr-only" @change="scanPhoto" />
        </label>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from "vue"
import { ErrorMessage, TextInput, call } from "frappe-ui"
import { BrowserMultiFormatReader } from "@zxing/browser"
import { BarcodeFormat, DecodeHintType } from "@zxing/library"
import { CameraOff, ImageUp } from "lucide-vue-next"
import { errorMessage } from "@/utils"

const show = defineModel({ type: Boolean })
const emit = defineEmits(["found"])

const video = ref(null)
const cameraOn = ref(false)
const cameraMessage = ref("Starting camera…")
const resolving = ref(false)
const error = ref("")
const manual = ref("")
const lastCode = ref("")

const hints = new Map([
  [
    DecodeHintType.POSSIBLE_FORMATS,
    [BarcodeFormat.QR_CODE, BarcodeFormat.EAN_13, BarcodeFormat.EAN_8, BarcodeFormat.UPC_A, BarcodeFormat.CODE_128],
  ],
])
const reader = new BrowserMultiFormatReader(hints)
let controls = null

async function startCamera() {
  error.value = ""
  cameraOn.value = false
  if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
    cameraMessage.value = "The camera needs a secure (https) connection. Scan from a photo or type the code instead."
    return
  }
  try {
    controls = await reader.decodeFromConstraints(
      { video: { facingMode: "environment" } },
      video.value,
      (result) => result && !resolving.value && lookup(result.getText()),
    )
    cameraOn.value = true
  } catch (err) {
    cameraMessage.value =
      err?.name === "NotAllowedError"
        ? "Camera access was blocked. Allow it in your browser, or scan from a photo."
        : "No camera found. Scan from a photo or type the code instead."
  }
}

function stopCamera() {
  controls?.stop()
  controls = null
  cameraOn.value = false
}

async function scanPhoto(event) {
  const file = event.target.files?.[0]
  event.target.value = ""
  if (!file) return
  const url = URL.createObjectURL(file)
  try {
    const result = await reader.decodeFromImageUrl(url)
    await lookup(result.getText())
  } catch {
    error.value = "No barcode or QR code found in that photo. Try a sharper, closer shot."
  } finally {
    URL.revokeObjectURL(url)
  }
}

async function lookup(code) {
  code = (code || "").trim()
  if (!code) return
  lastCode.value = code
  resolving.value = true
  error.value = ""
  try {
    const article = await call("library_management.api.resolve_article_code", { code })
    if (!article) {
      error.value = `No article matches "${code}". Check the ISBN is saved on the article.`
      return
    }
    emit("found", article)
    show.value = false
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    resolving.value = false
  }
}

watch(show, (open) => {
  if (open) {
    manual.value = ""
    error.value = ""
    setTimeout(startCamera, 50) // wait for the dialog to render the <video>
  } else {
    stopCamera()
  }
})
onBeforeUnmount(stopCamera)
</script>
