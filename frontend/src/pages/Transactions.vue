<template>
  <div class="pb-14">
    <PageHeader title="Transactions" subtitle="Every loan, from the day it goes out to the day it comes back.">
      <Button variant="solid" size="md" class="btn-room" @click="showIssue = true">
        <template #prefix><Plus class="size-4" /></template>
        Issue article
      </Button>
    </PageHeader>

    <div class="panel overflow-hidden">
      <div class="flex flex-wrap items-center gap-3 border-b border-paper-line px-5 py-3">
        <TabButtons v-model="tab" :buttons="tabs" />
        <TextInput v-model="query" placeholder="Search member or title" class="w-full sm:w-72">
          <template #prefix><Search class="size-4 text-ink-faint" /></template>
        </TextInput>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full min-w-[760px] text-left text-sm">
          <thead>
            <tr>
              <th class="th">Title</th>
              <th class="th">Member</th>
              <th class="th">Issued</th>
              <th class="th">Due</th>
              <th class="th">Status</th>
              <th class="th text-right">Fine</th>
              <th class="th w-24"><span class="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-paper-line">
            <tr v-for="row in transactions.data || []" :key="row.name" class="transition-colors hover:bg-paper/50">
              <td class="td">
                <p class="truncate font-medium text-ink">{{ row.article_title }}</p>
                <p class="text-xs text-ink-faint">{{ row.name }}</p>
              </td>
              <td class="td">
                <div class="flex items-center gap-2.5">
                  <Avatar :name="row.member_name" :seed="row.member" size="sm" />
                  <span class="truncate text-ink">{{ row.member_name }}</span>
                </div>
              </td>
              <td class="td text-ink-muted">{{ formatDate(row.issue_date) }}</td>
              <td class="td" :class="row.status === 'Overdue' ? 'font-medium text-brick' : 'text-ink-muted'">
                {{ row.status === "Returned" ? formatDate(row.return_date) : relativeDue(row.due_date) }}
              </td>
              <td class="td"><StatusBadge :status="row.status" /></td>
              <td class="td tnum text-right" :class="row.fine_amount ? 'font-medium text-brick' : 'text-ink-faint'">
                {{ row.fine_amount || "—" }}
              </td>
              <td class="td text-right">
                <Button
                  v-if="row.status !== 'Returned'"
                  size="sm"
                  :loading="returning === row.name"
                  @click="returnLoan(row)"
                >
                  Return
                </Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState
        v-if="transactions.data && !transactions.data.length"
        :icon="ArrowLeftRight"
        :title="emptyText"
        text="Issue an article to start a loan."
      />
    </div>
    <div v-if="transactions.hasNextPage" class="mt-6 flex justify-center">
      <Button :loading="transactions.list.loading" @click="transactions.next()">Show more loans</Button>
    </div>

    <IssueDialog v-model="showIssue" @issued="transactions.reload()" />
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue"
import { TabButtons, TextInput, call, createListResource, debounce, toast } from "frappe-ui"
import { ArrowLeftRight, Plus, Search } from "lucide-vue-next"
import PageHeader from "@/components/PageHeader.vue"
import StatusBadge from "@/components/StatusBadge.vue"
import Avatar from "@/components/Avatar.vue"
import EmptyState from "@/components/EmptyState.vue"
import IssueDialog from "@/components/IssueDialog.vue"
import { errorMessage, formatDate, relativeDue } from "@/utils"

const tabs = [
  { label: "On loan", value: "open" },
  { label: "Overdue", value: "Overdue" },
  { label: "Returned", value: "Returned" },
  { label: "All", value: "all" },
]
const tab = ref("open")
const query = ref("")
const showIssue = ref(false)
const returning = ref(null)

const emptyText = computed(() => {
  if (query.value) return "No loans match that search."
  return {
    open: "Nothing is out on loan right now.",
    Overdue: "No overdue loans. Everything is back on time.",
    Returned: "No articles have been returned yet.",
    all: "No loans yet. Issue an article to get started.",
  }[tab.value]
})

function filters() {
  const f = {}
  if (tab.value === "open") f.status = ["in", ["Issued", "Overdue"]]
  else if (tab.value !== "all") f.status = tab.value
  return f
}

function orFilters() {
  if (!query.value) return null
  const like = ["like", `%${query.value}%`]
  return { member_name: like, article_title: like, member: like, name: like }
}

const transactions = createListResource({
  doctype: "Library Transaction",
  fields: [
    "name",
    "member",
    "member_name",
    "article",
    "article_title",
        "issue_date",
    "due_date",
    "return_date",
    "status",
    "fine_amount",
  ],
  orderBy: "modified desc",
  pageLength: 50,
  filters: filters(),
  auto: true,
})

function refilter() {
  transactions.update({ filters: filters(), orFilters: orFilters(), start: 0 })
  transactions.reload()
}
watch(tab, refilter)
watch(query, debounce(refilter, 300))

async function returnLoan(row) {
  returning.value = row.name
  try {
    const doc = await call("library_management.api.return_article", { transaction: row.name })
    toast.success(doc.fine_amount ? `Returned. Fine due: ${doc.fine_amount}` : `${row.article_title} returned`)
    transactions.reload()
  } catch (err) {
    toast.error(errorMessage(err))
  } finally {
    returning.value = null
  }
}
</script>
