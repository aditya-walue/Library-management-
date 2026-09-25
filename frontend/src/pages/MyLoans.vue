<template>
  <div class="pb-14">
    <PageHeader :title="`${greeting()}${firstName ? ', ' + firstName : ''}`" :subtitle="subtitle">
      <Button size="md" @click="$router.push('/catalogue')">
        <template #prefix><BookOpen class="size-4" /></template>
        Browse catalogue
      </Button>
    </PageHeader>

    <div v-if="loaded && !member" class="panel">
      <EmptyState
        :icon="IdCard"
        title="You're not a library member yet"
        text="Ask a librarian to register you. You can still browse the catalogue."
      />
    </div>

    <div v-else class="space-y-6">
      <section class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div
          v-for="stat in tiles"
          :key="stat.label"
          class="panel p-5"
          :style="{ backgroundImage: `linear-gradient(135deg, ${stat.color}14 0%, #ffffff 60%)` }"
        >
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium" :style="{ color: stat.color }">{{ stat.label }}</p>
            <span
              class="flex size-9 items-center justify-center rounded-xl text-white"
              :style="{ backgroundColor: stat.color, boxShadow: `0 6px 14px -6px ${stat.color}` }"
            >
              <component :is="stat.icon" class="size-[18px]" :stroke-width="2" />
            </span>
          </div>
          <p class="tnum mt-3 font-display text-[2.4rem] font-medium leading-none text-ink">{{ loaded ? stat.value : "–" }}</p>
          <p class="mt-2 text-xs text-ink-muted">{{ loaded ? stat.hint : " " }}</p>
        </div>
      </section>

      <section class="panel overflow-hidden">
        <div class="panel-head">
          <h2 class="font-medium text-ink">On loan</h2>
        </div>
        <ul v-if="current.length" class="divide-y divide-paper-line">
          <li v-for="loan in current" :key="loan.name" class="flex flex-wrap items-center gap-3 px-5 py-3.5">
            <div class="min-w-0 flex-1">
              <p class="truncate font-medium text-ink">{{ loan.article_title }}</p>
              <p class="text-sm text-ink-muted">Borrowed {{ formatDate(loan.issue_date) }} · due {{ formatDate(loan.due_date) }}</p>
            </div>
            <span
              class="shrink-0 rounded-full px-2 py-0.5 text-xs font-medium"
              :class="loan.status === 'Overdue' ? 'bg-[#D9485F]/10 text-[#C23A50]' : 'bg-[#2F6FE4]/10 text-[#2F6FE4]'"
            >
              {{ relativeDue(loan.due_date) }}
            </span>
            <span v-if="loan.fine_amount" class="tnum shrink-0 text-sm font-medium text-[#C23A50]">
              Fine {{ formatFine(loan.fine_amount) }} so far
            </span>
          </li>
        </ul>
        <EmptyState
          v-else-if="loaded"
          :icon="BookMarked"
          title="Nothing on loan"
          text="Find a title in the catalogue and ask a librarian to issue it."
        />
      </section>

      <section v-if="history.length" class="panel overflow-hidden">
        <div class="panel-head">
          <h2 class="font-medium text-ink">History</h2>
          <span class="text-sm text-ink-muted">{{ history.length }} returned</span>
        </div>
        <ul class="divide-y divide-paper-line">
          <li v-for="loan in history" :key="loan.name" class="flex items-center gap-3 px-5 py-3 text-sm">
            <p class="min-w-0 flex-1 truncate font-medium text-ink">{{ loan.article_title }}</p>
            <span class="shrink-0 text-ink-muted">Returned {{ formatDate(loan.return_date) }}</span>
            <span v-if="loan.fine_amount" class="tnum w-20 shrink-0 text-right text-[#C23A50]">
              Fine {{ formatFine(loan.fine_amount) }}
            </span>
            <span v-else class="w-20 shrink-0" />
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { createResource } from "frappe-ui"
import { AlertTriangle, BookMarked, BookOpen, IdCard, Receipt } from "lucide-vue-next"
import PageHeader from "@/components/PageHeader.vue"
import EmptyState from "@/components/EmptyState.vue"
import { formatDate, formatFine, greeting, relativeDue } from "@/utils"

const firstName = (window.full_name || "").split(" ")[0]

const mine = createResource({ url: "library_management.api.get_my_loans", auto: true })
const loaded = computed(() => !!mine.data)
const member = computed(() => mine.data?.member)
const loans = computed(() => mine.data?.loans || [])
const current = computed(() => loans.value.filter((l) => l.status !== "Returned"))
const history = computed(() => loans.value.filter((l) => l.status === "Returned"))

const subtitle = computed(() =>
  member.value ? `${member.value.membership_type} member since ${formatDate(member.value.joined_on)}` : "",
)

const tiles = computed(() => {
  const overdue = current.value.filter((l) => l.status === "Overdue")
  const fines = loans.value.reduce((sum, l) => sum + (l.fine_amount || 0), 0)
  const nextDue = current.value
    .filter((l) => l.status !== "Overdue")
    .sort((a, b) => (a.due_date > b.due_date ? 1 : -1))[0]
  return [
    {
      label: "On loan",
      value: current.value.length,
      hint: nextDue ? `Next: ${relativeDue(nextDue.due_date).toLowerCase()}` : "Nothing due",
      icon: BookMarked,
      color: "#2F6FE4",
    },
    {
      label: "Overdue",
      value: overdue.length,
      hint: overdue.length ? "Please return these soon" : "You're all on time",
      icon: AlertTriangle,
      color: "#D9485F",
    },
    {
      label: "Fines",
      value: formatFine(fines),
      hint: fines ? "Pay at the library desk" : "No fines",
      icon: Receipt,
      color: "#B7791F",
    },
  ]
})
</script>
