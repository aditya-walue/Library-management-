<template>
  <div class="pb-14">
    <PageHeader :title="`${greeting()}${firstName ? ', ' + firstName : ''}`" :subtitle="today">
      <Button variant="solid" size="md" class="btn-room" @click="showIssue = true">
        <template #prefix><Plus class="size-4" /></template>
        Issue article
      </Button>
    </PageHeader>

    <div class="space-y-6">
      <section class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div
          v-for="stat in tiles"
          :key="stat.label"
          class="panel relative overflow-hidden p-5"
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
          <p class="tnum mt-3 font-display text-[2.4rem] font-medium leading-none text-ink">
            {{ loaded ? stat.value : "–" }}
          </p>
          <p class="mt-2 text-xs text-ink-muted">{{ loaded ? stat.hint : "\u00a0" }}</p>
        </div>
      </section>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section class="panel overflow-hidden lg:col-span-2">
          <div class="panel-head">
            <h2 class="font-medium text-ink">Due back soon</h2>
            <router-link to="/transactions" class="text-sm text-ink-muted hover:text-ink">View all loans</router-link>
          </div>
          <ul v-if="data.due_soon?.length" class="divide-y divide-paper-line">
            <li v-for="loan in data.due_soon" :key="loan.name" class="flex items-center gap-3 px-5 py-3.5">
              <Avatar :name="loan.member_name" :seed="loan.member" />
              <div class="min-w-0 flex-1">
                <p class="truncate font-medium text-ink">{{ loan.article_title }}</p>
                <p class="truncate text-sm text-ink-muted">{{ loan.member_name }}</p>
              </div>
              <span
                class="shrink-0 rounded-full px-2 py-0.5 text-xs font-medium"
                :class="loan.status === 'Overdue' ? 'bg-[#D9485F]/10 text-[#C23A50]' : 'bg-[#2F6FE4]/10 text-[#2F6FE4]'"
              >
                {{ relativeDue(loan.due_date) }}
              </span>
              <Button size="sm" :loading="returning === loan.name" @click="returnLoan(loan)">Return</Button>
            </li>
          </ul>
          <EmptyState
            v-else-if="loaded"
            :icon="CalendarCheck"
            title="Nothing due soon"
            text="Loans due in the next three days will appear here."
          />
        </section>

        <section class="panel overflow-hidden">
          <div class="panel-head">
            <h2 class="font-medium text-ink">Catalogue mix</h2>
            <span class="tnum text-sm text-ink-muted">{{ data.articles ?? 0 }} titles</span>
          </div>
          <ul v-if="data.by_category?.length" class="space-y-3.5 px-5 py-5">
            <li v-for="c in data.by_category" :key="c.category">
              <div class="flex justify-between text-sm">
                <span class="flex items-center gap-2 text-ink">
                  <span class="size-2 rounded-full" :style="{ backgroundColor: colorFor(c.category) }" />
                  {{ c.category }}
                </span>
                <span class="tnum text-ink-muted">{{ c.count }}</span>
              </div>
              <div class="mt-1.5 h-1.5 rounded-full" :style="{ backgroundColor: tintFor(c.category, '1F') }">
                <div
                  class="h-1.5 rounded-full"
                  :style="{ width: `${(c.count / maxCategory) * 100}%`, backgroundColor: colorFor(c.category) }"
                />
              </div>
            </li>
          </ul>
          <EmptyState v-else-if="loaded" :icon="BookOpen" title="No titles yet" text="Add articles to the catalogue." />
        </section>
      </div>

      <section class="panel overflow-hidden">
        <div class="panel-head">
          <h2 class="font-medium text-ink">Recent activity</h2>
        </div>
        <ul v-if="data.recent?.length" class="divide-y divide-paper-line">
          <li v-for="t in data.recent" :key="t.name" class="flex items-center gap-3 px-5 py-3 text-sm">
            <span
              class="flex size-8 shrink-0 items-center justify-center rounded-full"
              :class="t.status === 'Returned' ? 'bg-[#0F9F6E]/10 text-[#0F9F6E]' : t.status === 'Overdue' ? 'bg-[#D9485F]/10 text-[#D9485F]' : 'bg-[#2F6FE4]/10 text-[#2F6FE4]'"
            >
              <component :is="t.status === 'Returned' ? ArrowDownLeft : ArrowUpRight" class="size-4" :stroke-width="2" />
            </span>
            <p class="min-w-0 flex-1 truncate text-ink-muted">
              <span class="font-medium text-ink">{{ t.member_name }}</span>
              {{ t.status === "Returned" ? "returned" : "borrowed" }}
              <span class="font-medium text-ink">{{ t.article_title }}</span>
            </p>
            <span class="shrink-0 text-xs text-ink-faint">{{ ago(t.modified) }}</span>
          </li>
        </ul>
        <EmptyState
          v-else-if="loaded"
          :icon="History"
          title="No activity yet"
          text="Issued and returned articles will show up here."
        />
      </section>
    </div>

    <IssueDialog v-model="showIssue" @issued="stats.reload()" />
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { call, createResource, dayjs, toast } from "frappe-ui"
import {
  AlertTriangle,
  ArrowDownLeft,
  ArrowUpRight,
  BookOpen,
  CalendarCheck,
  History,
  Library,
  Plus,
  Users,
} from "lucide-vue-next"
import PageHeader from "@/components/PageHeader.vue"
import Avatar from "@/components/Avatar.vue"
import EmptyState from "@/components/EmptyState.vue"
import IssueDialog from "@/components/IssueDialog.vue"
import { colorFor, errorMessage, greeting, relativeDue, tintFor } from "@/utils"

const today = dayjs().format("dddd, D MMMM")
const firstName = (window.full_name || "").split(" ")[0]
const showIssue = ref(false)
const returning = ref(null)

const stats = createResource({ url: "library_management.api.get_dashboard_stats", auto: true })
const data = computed(() => stats.data || {})
const loaded = computed(() => !!stats.data)
const maxCategory = computed(() => Math.max(1, ...(data.value.by_category || []).map((c) => c.count)))

const tiles = computed(() => {
  const d = data.value
  const pct = d.copies ? Math.round((d.available / d.copies) * 100) : 0
  const dueSoon = (d.due_soon || []).filter((l) => l.status !== "Overdue").length
  return [
    {
      label: "On the shelf",
      value: d.available,
      hint: `${pct}% of ${d.copies ?? 0} copies across ${d.articles ?? 0} titles`,
      icon: Library,
      color: "#0F9F6E",
    },
    {
      label: "On loan",
      value: d.issued,
      hint: dueSoon ? `${dueSoon} due in the next three days` : "None due in the next three days",
      icon: ArrowUpRight,
      color: "#2F6FE4",
    },
    {
      label: "Overdue",
      value: d.overdue,
      hint: d.overdue ? "Follow up with these members" : "Everything is back on time",
      icon: AlertTriangle,
      color: "#D9485F",
    },
    {
      label: "Active members",
      value: d.members,
      hint: "Able to borrow today",
      icon: Users,
      color: "#7C5CE0",
    },
  ]
})

function ago(value) {
  const mins = dayjs().diff(dayjs(value), "minute")
  if (mins < 1) return "Just now"
  if (mins < 60) return `${mins} min ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} h ago`
  return dayjs(value).format("D MMM")
}

async function returnLoan(loan) {
  returning.value = loan.name
  try {
    const doc = await call("library_management.api.return_article", { transaction: loan.name })
    toast.success(doc.fine_amount ? `Returned. Fine due: ${doc.fine_amount}` : "Returned")
    stats.reload()
  } catch (err) {
    toast.error(errorMessage(err))
  } finally {
    returning.value = null
  }
}
</script>
