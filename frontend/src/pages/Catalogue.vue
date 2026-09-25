<template>
  <div class="pb-14">
    <PageHeader title="Catalogue" :subtitle="isStaff ? 'Every title the library owns, with live availability.' : 'Browse the library. Ask a librarian to borrow a title.'">
      <Button v-if="isStaff" variant="solid" size="md" class="btn-room" @click="openArticle(null)">
        <template #prefix><Plus class="size-4" /></template>
        Add article
      </Button>
    </PageHeader>

    <div class="panel overflow-hidden">
      <div class="flex flex-wrap items-center gap-3 border-b border-paper-line px-5 py-3">
        <TextInput v-model="query" placeholder="Search title, author or barcode" class="w-full sm:w-80">
          <template #prefix><Search class="size-4 text-ink-faint" /></template>
        </TextInput>
        <ScanButton label="Scan" size="md" @found="showScanned" />
        <FormControl v-model="category" type="select" :options="categoryOptions" class="w-44" />
        <Switch v-model="availableOnly" label="Available only" />
      </div>
      <div v-if="scanned" class="flex items-center justify-between gap-3 border-b border-paper-line bg-[#2F6FE4]/5 px-5 py-2.5 text-sm">
        <span class="text-ink">Showing the scanned article</span>
        <button class="font-medium text-[#2F6FE4] hover:underline" @click="clearScanned">Show all titles</button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full min-w-[680px] text-left text-sm">
          <thead>
            <tr>
              <th class="th">Title</th>
              <th class="th">Category</th>
              <th class="th hidden md:table-cell">ISBN / Barcode</th>
              <th class="th w-44">Availability</th>
              <th v-if="isStaff" class="th w-36"><span class="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-paper-line">
            <tr v-for="a in results.data || []" :key="a.name" class="group transition-colors hover:bg-paper/50">
              <td class="td">
                <div class="flex items-center gap-3">
                  <span
                    class="flex h-10 w-8 shrink-0 items-center justify-center rounded-md"
                    :style="{ backgroundColor: tintFor(a.category), color: colorFor(a.category) }"
                  >
                    <BookOpen class="size-4" :stroke-width="1.75" />
                  </span>
                  <div class="min-w-0">
                    <p class="truncate font-medium text-ink">{{ a.title }}</p>
                    <p class="truncate text-ink-muted">{{ a.author }}</p>
                  </div>
                </div>
              </td>
              <td class="td"><CategoryPill :category="a.category" /></td>
              <td class="td hidden text-ink-muted md:table-cell">{{ a.isbn || "—" }}</td>
              <td class="td">
                <div class="flex items-center gap-3">
                  <div class="h-1.5 flex-1 rounded-full bg-[#0F9F6E]/10">
                    <div
                      class="h-1.5 rounded-full"
                      :class="a.available_copies ? 'bg-[#0F9F6E]' : 'bg-[#D9485F]'"
                      :style="{ width: `${a.total_copies ? Math.max((a.available_copies / a.total_copies) * 100, a.available_copies ? 0 : 100) : 0}%` }"
                    />
                  </div>
                  <span class="tnum w-10 text-right text-xs" :class="a.available_copies ? 'text-ink' : 'text-brick'">
                    {{ a.available_copies }}/{{ a.total_copies }}
                  </span>
                </div>
              </td>
              <td v-if="isStaff" class="td">
                <div class="flex justify-end gap-1.5">
                  <Button size="sm" variant="ghost" @click="openArticle(a)">Edit</Button>
                  <Button size="sm" :disabled="!a.available_copies" @click="issue(a)">Issue</Button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState
        v-if="results.data && !results.data.length"
        :icon="BookOpen"
        :title="filtered ? 'No matching titles' : 'The catalogue is empty'"
        :text="filtered ? 'Try a shorter search or another category.' : isStaff ? 'Add the first title to start lending.' : 'Check back soon for new titles.'"
      >
        <Button v-if="filtered" size="sm" @click="clearFilters">Clear search</Button>
      </EmptyState>
    </div>

    <div v-if="hasMore" class="mt-6 flex justify-center">
      <Button :loading="results.loading" @click="loadMore">Show more</Button>
    </div>

    <ArticleDialog v-if="isStaff" v-model="showArticle" :doc="editing" @saved="search" />
    <IssueDialog v-if="isStaff" v-model="showIssue" :article="issuing" @issued="search" />
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { Switch, TextInput, createResource, debounce } from "frappe-ui"
import { BookOpen, Plus, Search } from "lucide-vue-next"
import PageHeader from "@/components/PageHeader.vue"
import EmptyState from "@/components/EmptyState.vue"
import ScanButton from "@/components/ScanButton.vue"
import ArticleDialog from "@/components/ArticleDialog.vue"
import IssueDialog from "@/components/IssueDialog.vue"
import { categories, colorFor, isStaff, tintFor } from "@/utils"
import CategoryPill from "@/components/CategoryPill.vue"

const PAGE = 50
const route = useRoute()
const router = useRouter()
const query = ref(route.query.q || "")
const category = ref("all")
const availableOnly = ref(false)
const hasMore = ref(false)
const scanned = ref(route.query.article || "")
const filtered = computed(() => !!(query.value || category.value !== "all" || availableOnly.value || scanned.value))
const categoryOptions = [{ label: "All categories", value: "all" }, ...categories.map((c) => ({ label: c, value: c }))]

const showArticle = ref(false)
const editing = ref(null)
const showIssue = ref(false)
const issuing = ref(null)

const results = createResource({
  url: "library_management.api.search_catalogue",
  makeParams: ({ start = 0 } = {}) => ({
    query: query.value,
    category: category.value === "all" ? "" : category.value,
    available_only: availableOnly.value ? 1 : 0,
    article: scanned.value || undefined,
    start,
    page_length: PAGE,
  }),
  transform(data) {
    hasMore.value = data.length === PAGE
    return data
  },
})

function search() {
  results.fetch({ start: 0 })
}

async function loadMore() {
  const previous = results.data || []
  await results.fetch({ start: previous.length })
  results.setData([...previous, ...results.data])
}

function showScanned(article) {
  router.replace({ query: { article: article.name } })
}

function clearScanned() {
  router.replace({ query: {} })
}

watch(
  () => route.query.article,
  (article) => {
    scanned.value = article || ""
    search()
  },
)

function clearFilters() {
  clearScanned()
  query.value = ""
  category.value = "all"
  availableOnly.value = false
}

watch(query, debounce(search, 300))
watch([category, availableOnly], search)
search()

function openArticle(article) {
  editing.value = article
  showArticle.value = true
}

function issue(article) {
  issuing.value = article.name
  showIssue.value = true
}
</script>
