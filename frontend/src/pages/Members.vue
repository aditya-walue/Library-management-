<template>
  <div class="pb-14">
    <PageHeader title="Members" subtitle="People who can borrow, each linked to their user account.">
      <Button variant="solid" size="md" class="btn-room" @click="editMember(null)">
        <template #prefix><Plus class="size-4" /></template>
        New member
      </Button>
    </PageHeader>

    <div class="panel overflow-hidden">
      <div class="flex flex-wrap items-center gap-3 border-b border-paper-line px-5 py-3">
        <TextInput v-model="query" placeholder="Search by name" class="w-full sm:w-72">
          <template #prefix><Search class="size-4 text-ink-faint" /></template>
        </TextInput>
        <ScanButton kind="member" label="Scan ID card" size="md" @found="openMember" />
        <TabButtons v-model="status" :buttons="[{ label: 'Active' }, { label: 'Inactive' }, { label: 'All', value: '' }]" />
      </div>
      <div class="overflow-x-auto">
        <table class="w-full min-w-[560px] text-left text-sm">
          <thead>
            <tr>
              <th class="th">Member</th>
              <th class="th">Membership</th>
              <th class="th hidden md:table-cell">ID card</th>
              <th class="th hidden lg:table-cell">Phone</th>
              <th class="th hidden md:table-cell">Joined</th>
              <th class="th text-right">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-paper-line">
            <tr
              v-for="m in members.data || []"
              :key="m.name"
              tabindex="0"
              class="cursor-pointer transition-colors hover:bg-paper/50 focus-visible:bg-paper/50"
              @click="openMember(m)"
              @keydown.enter="openMember(m)"
            >
              <td class="td">
                <div class="flex items-center gap-3">
                  <Avatar :name="m.full_name" :seed="m.name" />
                  <div class="min-w-0">
                    <p class="truncate font-medium text-ink">{{ m.full_name }}</p>
                    <p class="truncate text-xs text-ink-muted">{{ m.user }}</p>
                  </div>
                </div>
              </td>
              <td class="td text-ink-muted">{{ m.membership_type }}</td>
              <td class="td hidden text-ink-muted md:table-cell">{{ m.card_id || "—" }}</td>
              <td class="td hidden text-ink-muted lg:table-cell">{{ m.phone || "—" }}</td>
              <td class="td hidden text-ink-muted md:table-cell">{{ formatDate(m.joined_on) }}</td>
              <td class="td text-right"><StatusBadge :status="m.status" /></td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState
        v-if="members.data && !members.data.length"
        :icon="Users"
        :title="query ? 'No matching members' : 'No members here'"
        :text="query ? 'Try a different name.' : 'Add a member to start lending.'"
      />
    </div>
    <div v-if="members.hasNextPage" class="mt-6 flex justify-center">
      <Button :loading="members.list.loading" @click="members.next()">Show more members</Button>
    </div>

    <Dialog v-model="showDetail" :options="{ size: '2xl' }">
      <template #body>
        <div v-if="selected" class="p-6">
          <div class="flex items-start gap-4">
            <Avatar :name="selected.full_name" :seed="selected.name" size="lg" />
            <div class="min-w-0 flex-1">
              <h2 class="font-display text-2xl font-medium text-ink">{{ selected.full_name }}</h2>
              <p class="text-sm text-ink-muted">
                {{ selected.user }}<template v-if="selected.card_id"> · ID card {{ selected.card_id }}</template>
              </p>
              <div class="mt-2 flex flex-wrap items-center gap-2 text-sm text-ink-muted">
                <StatusBadge :status="selected.status" />
                <span>{{ selected.membership_type }} member since {{ formatDate(selected.joined_on) }}</span>
              </div>
            </div>
          </div>

          <LibraryCard :member="selected" class="mt-5" />

          <h3 class="mb-2 mt-6 text-sm font-medium text-ink">Loans</h3>
          <ul v-if="loans.data?.length" class="divide-y divide-paper-line rounded-xl border border-paper-line">
            <li v-for="loan in loans.data" :key="loan.name" class="flex items-center gap-3 px-4 py-3">
              <div class="min-w-0 flex-1">
                <p class="truncate font-medium text-ink">{{ loan.article_title }}</p>
                <p class="text-xs text-ink-muted">
                  Issued {{ formatDate(loan.issue_date) }} ·
                  {{ loan.status === "Returned" ? `returned ${formatDate(loan.return_date)}` : relativeDue(loan.due_date) }}
                  <span v-if="loan.fine_amount" class="font-medium text-[#C23A50]">
                    · Fine {{ formatFine(loan.fine_amount) }}{{ loan.status === "Overdue" ? " so far" : "" }}
                  </span>
                </p>
              </div>
              <StatusBadge :status="loan.status" />
              <Button
                v-if="loan.status !== 'Returned'"
                size="sm"
                :loading="returning === loan.name"
                @click="returnLoan(loan)"
              >
                Return
              </Button>
            </li>
          </ul>
          <p v-else class="rounded-xl border border-dashed border-paper-line px-4 py-6 text-center text-sm text-ink-muted">
            {{ selected.full_name.split(" ")[0] }} hasn't borrowed anything yet.
          </p>

          <div class="mt-6 flex justify-end gap-2">
            <Button @click="editMember(selected)">Edit member</Button>
            <Button variant="solid" class="btn-room" :disabled="selected.status !== 'Active'" @click="showIssue = true">
              Issue article
            </Button>
          </div>
        </div>
      </template>
    </Dialog>

    <MemberDialog v-model="showEdit" :doc="editing" @saved="members.reload()" />
    <IssueDialog v-model="showIssue" :member="selected?.name" @issued="loadLoans" />
  </div>
</template>

<script setup>
import { ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { TabButtons, TextInput, call, createListResource, createResource, debounce, toast } from "frappe-ui"
import { Plus, Search, Users } from "lucide-vue-next"
import PageHeader from "@/components/PageHeader.vue"
import StatusBadge from "@/components/StatusBadge.vue"
import Avatar from "@/components/Avatar.vue"
import EmptyState from "@/components/EmptyState.vue"
import ScanButton from "@/components/ScanButton.vue"
import LibraryCard from "@/components/LibraryCard.vue"
import MemberDialog from "@/components/MemberDialog.vue"
import IssueDialog from "@/components/IssueDialog.vue"
import { errorMessage, formatDate, formatFine, relativeDue } from "@/utils"

const route = useRoute()
const router = useRouter()
const query = ref("")
const status = ref("Active")

const filters = () => {
  const f = {}
  if (status.value) f.status = status.value
  if (query.value) f.full_name = ["like", `%${query.value}%`]
  return f
}

const members = createListResource({
  doctype: "Library Member",
  fields: ["name", "user", "card_id", "full_name", "email", "phone", "membership_type", "status", "joined_on"],
  orderBy: "full_name asc",
  pageLength: 50,
  filters: filters(),
  auto: true,
})

function refilter() {
  members.update({ filters: filters(), start: 0 })
  members.reload()
}
watch(query, debounce(refilter, 300))
watch(status, refilter)

const selected = ref(null)
const showDetail = ref(false)
const showEdit = ref(false)
const showIssue = ref(false)
const editing = ref(null)
const returning = ref(null)

const loans = createResource({
  url: "frappe.client.get_list",
  makeParams: ({ member }) => ({
    doctype: "Library Transaction",
    filters: { member },
    fields: ["name", "article_title", "issue_date", "due_date", "return_date", "status", "fine_amount"],
    order_by: "issue_date desc",
    limit_page_length: 100,
  }),
})
const loadLoans = () => selected.value && loans.fetch({ member: selected.value.name })

function openMember(row) {
  selected.value = row
  loans.setData([])
  loadLoans()
  showDetail.value = true
}

// library card QR links open straight into the member's profile
async function openFromLink(code) {
  if (!code) return
  const member = await call("library_management.api.resolve_member_code", { code }).catch(() => null)
  if (member) openMember(member)
  else toast.error("That library card doesn't match any member.")
  router.replace({ query: {} })
}
watch(() => route.query.member, openFromLink, { immediate: true })

function editMember(member) {
  editing.value = member
  showDetail.value = false
  showEdit.value = true
}

async function returnLoan(loan) {
  returning.value = loan.name
  try {
    const doc = await call("library_management.api.return_article", { transaction: loan.name })
    toast.success(doc.fine_amount ? `Returned. Fine due: ${formatFine(doc.fine_amount)}` : "Returned")
    loadLoans()
  } catch (err) {
    toast.error(errorMessage(err))
  } finally {
    returning.value = null
  }
}
</script>
