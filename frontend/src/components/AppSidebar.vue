<template>
  <aside class="hidden w-56 shrink-0 flex-col border-r border-paper-line bg-white md:flex">
    <div class="flex items-center gap-2.5 px-5 pb-6 pt-6">
      <span class="flex size-7 items-center justify-center rounded-md bg-room text-white">
        <BookOpen class="size-4" :stroke-width="2" />
      </span>
      <span class="font-display text-lg font-medium text-ink">Library</span>
    </div>

    <nav class="flex flex-col gap-0.5 px-3">
      <router-link
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-ink-muted transition-colors hover:bg-paper hover:text-ink"
        :class="isActive(item) && 'bg-room-soft font-medium !text-room'"
      >
        <component :is="item.icon" class="size-4" :stroke-width="1.75" />
        <span class="flex-1">{{ item.label }}</span>
        <span
          v-if="item.to === '/transactions' && overdue.data"
          class="tnum rounded-full bg-brick-soft px-1.5 text-[11px] font-semibold leading-5 text-brick"
          :title="`${overdue.data} overdue`"
        >
          {{ overdue.data }}
        </span>
      </router-link>
    </nav>

    <div class="mt-auto border-t border-paper-line p-3">
      <a v-if="isStaff" href="/app/library" class="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-ink-muted hover:bg-paper hover:text-ink">
        <Monitor class="size-4" :stroke-width="1.75" />
        Open in Desk
      </a>
      <div class="flex items-center gap-3 px-3 py-2">
        <Avatar :name="user" size="sm" />
        <span class="min-w-0 flex-1 truncate text-sm text-ink">{{ user }}</span>
        <button class="rounded p-1 text-ink-faint hover:text-ink" title="Log out" aria-label="Log out" @click="logout">
          <LogOut class="size-4" :stroke-width="1.75" />
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from "vue-router"
import { BookOpen, LogOut, Monitor } from "lucide-vue-next"
import { call, createResource } from "frappe-ui"
import Avatar from "@/components/Avatar.vue"
import { isStaff } from "@/utils"

const overdue = createResource({
  url: "frappe.client.get_count",
  params: { doctype: "Library Transaction", filters: { status: "Overdue" } },
  auto: isStaff,
  cache: "overdue-count",
})

defineProps({ items: Array })
const route = useRoute()
const user = window.full_name || window.user || ""
async function logout() {
  await call("logout").catch(() => {})
  window.location.href = "/login"
}

const isActive = (item) => (item.to === "/" ? route.path === "/" : route.path.startsWith(item.to))
</script>
