<template>
  <Dialog v-model="show" :options="{ title: doc ? 'Edit member' : 'New member', size: 'lg' }">
    <template #body-content>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="sm:col-span-2">
          <label class="mb-1.5 block text-xs text-ink-gray-5">User</label>
          <FormControl v-if="doc" :model-value="doc.user" disabled />
          <Combobox
            v-else
            v-model="form.user"
            :options="userOptions"
            placeholder="Search users by name or email"
            open-on-focus
            @input="searchUsers"
          />
          <p class="mt-1.5 text-xs text-ink-gray-5">
            Name and email come from the user record. Members are identified by their user ID.
          </p>
        </div>
        <FormControl :model-value="selectedUser?.full_name" label="Full name" disabled />
        <FormControl :model-value="selectedUser?.email" label="Email" disabled />
        <FormControl v-model="form.phone" label="Phone" />
        <FormControl
          v-model="form.membership_type"
          type="select"
          :options="['Student', 'Faculty', 'Public']"
          label="Membership type"
        />
        <FormControl v-model="form.status" type="select" :options="['Active', 'Inactive']" label="Status" />
        <ErrorMessage :message="error" class="sm:col-span-2" />
      </div>
    </template>
    <template #actions>
      <Button variant="solid" class="btn-room w-full" :loading="saving" :disabled="!form.user" @click="save">
        {{ doc ? "Save changes" : "Add member" }}
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue"
import { Combobox, ErrorMessage, call, createResource, debounce, toast } from "frappe-ui"
import { errorMessage } from "@/utils"

const props = defineProps({ doc: Object })
const show = defineModel({ type: Boolean })
const emit = defineEmits(["saved"])

const fields = ["user", "phone", "membership_type", "status"]
const blank = { membership_type: "Public", status: "Active" }
const form = reactive({})
const error = ref("")
const saving = ref(false)

const users = createResource({
  url: "library_management.api.get_unlinked_users",
  makeParams: ({ txt = "" } = {}) => ({ txt }),
})
const searchUsers = debounce((txt) => users.fetch({ txt }), 300)

const userOptions = computed(() =>
  (users.data || []).map((u) => ({ label: `${u.full_name || u.name} · ${u.name}`, value: u.name })),
)

const selectedUser = computed(() => {
  if (props.doc) return props.doc
  return (users.data || []).find((u) => u.name === form.user)
})

watch(show, (open) => {
  if (!open) return
  error.value = ""
  for (const key of fields) form[key] = props.doc?.[key] ?? blank[key] ?? ""
  if (!props.doc) {
    form.user = null
    users.fetch({ txt: "" })
  }
})

async function save() {
  saving.value = true
  error.value = ""
  try {
    const doc = props.doc
      ? await call("frappe.client.set_value", {
          doctype: "Library Member",
          name: props.doc.name,
          fieldname: { phone: form.phone, membership_type: form.membership_type, status: form.status },
        })
      : await call("frappe.client.insert", { doc: { doctype: "Library Member", ...form } })
    toast.success(props.doc ? "Member updated" : `${doc.full_name} added`)
    show.value = false
    emit("saved", doc)
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    saving.value = false
  }
}
</script>
