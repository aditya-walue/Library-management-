<template>
  <Dialog v-model="show" :options="{ title: doc ? 'Edit article' : 'Add article', size: 'xl' }">
    <template #body-content>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormControl v-model="form.title" label="Title" class="sm:col-span-2" required />
        <FormControl v-model="form.author" label="Author" required />
        <FormControl v-model="form.isbn" label="ISBN / Barcode" />
        <FormControl v-model="form.category" type="select" :options="categories" label="Category" />
        <FormControl v-model="form.publisher" label="Publisher" />
        <FormControl v-model="form.published_year" type="number" label="Published year" />
        <FormControl v-model="form.total_copies" type="number" label="Total copies" />
        <FormControl v-model="form.description" type="textarea" label="Description" class="sm:col-span-2" />
        <ArticleQR v-if="doc" :article="doc" class="sm:col-span-2" />
        <ErrorMessage :message="error" class="sm:col-span-2" />
      </div>
    </template>
    <template #actions>
      <Button variant="solid" class="btn-room w-full" :loading="saving" :disabled="!form.title || !form.author" @click="save">
        {{ doc ? "Save changes" : "Add article" }}
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { reactive, ref, watch } from "vue"
import { ErrorMessage, call, toast } from "frappe-ui"
import { categories, errorMessage } from "@/utils"
import ArticleQR from "@/components/ArticleQR.vue"

const props = defineProps({ doc: Object })
const show = defineModel({ type: Boolean })
const emit = defineEmits(["saved"])

const fields = ["title", "author", "isbn", "category", "publisher", "published_year", "total_copies", "description"]
const blank = { category: "Other", total_copies: 1 }
const form = reactive({})
const error = ref("")
const saving = ref(false)

watch(show, (open) => {
  if (!open) return
  error.value = ""
  for (const key of fields) form[key] = props.doc?.[key] ?? blank[key] ?? ""
  if (!form.published_year) form.published_year = ""
})

async function save() {
  saving.value = true
  error.value = ""
  const values = { ...form, total_copies: Number(form.total_copies) || 0, published_year: Number(form.published_year) || null }
  try {
    const doc = props.doc
      ? await call("frappe.client.set_value", { doctype: "Library Article", name: props.doc.name, fieldname: values })
      : await call("frappe.client.insert", { doc: { doctype: "Library Article", ...values } })
    toast.success(props.doc ? "Article updated" : "Article added")
    show.value = false
    emit("saved", doc)
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    saving.value = false
  }
}
</script>
