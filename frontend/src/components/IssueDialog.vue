<template>
  <Dialog v-model="show" :options="{ title: 'Issue article', size: 'lg' }">
    <template #body-content>
      <div class="space-y-4">
        <div>
          <label class="mb-1.5 block text-xs text-ink-gray-5">Member</label>
          <Combobox
            v-model="form.member"
            :options="memberOptions"
            placeholder="Search active members"
            open-on-focus
          />
        </div>
        <div>
          <label class="mb-1.5 block text-xs text-ink-gray-5">Article</label>
          <Combobox
            v-model="form.article"
            :options="articleOptions"
            placeholder="Search available articles"
            open-on-focus
          />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <FormControl v-model="form.issue_date" type="date" label="Issue date" />
          <FormControl
            v-model="form.due_date"
            type="date"
            label="Due date"
            :description="'Leave blank to use the default loan period'"
          />
        </div>
        <ErrorMessage :message="error" />
      </div>
    </template>
    <template #actions>
      <Button
        variant="solid"
        class="btn-room w-full"
        :loading="issue.loading"
        :disabled="!form.member || !form.article"
        @click="submit"
      >
        Issue article
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue"
import { Combobox, ErrorMessage, createListResource, createResource, dayjs, toast } from "frappe-ui"
import { errorMessage } from "@/utils"

const props = defineProps({ member: String, article: String })
const show = defineModel({ type: Boolean })
const emit = defineEmits(["issued"])

const today = () => dayjs().format("YYYY-MM-DD")
const form = reactive({ member: null, article: null, issue_date: today(), due_date: "" })
const error = ref("")

const members = createListResource({
  doctype: "Library Member",
  fields: ["name", "full_name", "email"],
  filters: { status: "Active" },
  orderBy: "full_name asc",
  pageLength: 1000,
})
const articles = createListResource({
  doctype: "Library Article",
  fields: ["name", "title", "author", "available_copies"],
  filters: { available_copies: [">", 0] },
  orderBy: "title asc",
  pageLength: 1000,
})

const memberOptions = computed(() =>
  (members.data || []).map((m) => ({ label: `${m.full_name} · ${m.name}`, value: m.name })),
)
const articleOptions = computed(() =>
  (articles.data || []).map((a) => ({
    label: `${a.title} — ${a.author} (${a.available_copies} left)`,
    value: a.name,
  })),
)

watch(show, (open) => {
  if (!open) return
  Object.assign(form, { member: props.member || null, article: props.article || null, issue_date: today(), due_date: "" })
  error.value = ""
  members.reload()
  articles.reload()
})

const issue = createResource({
  url: "library_management.api.issue_article",
  onSuccess(doc) {
    toast.success(`Issued to ${doc.member_name}, due ${dayjs(doc.due_date).format("D MMM")}`)
    show.value = false
    emit("issued", doc)
  },
  onError(err) {
    error.value = errorMessage(err)
  },
})

function submit() {
  error.value = ""
  issue.submit({ ...form, due_date: form.due_date || null })
}
</script>
