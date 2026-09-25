<template>
  <FrappeUIProvider>
    <div class="flex h-screen w-screen bg-paper">
      <AppSidebar :items="navItems" />
      <div class="flex min-w-0 flex-1 flex-col">
        <nav class="flex items-center gap-1 overflow-x-auto border-b border-paper-line bg-white px-3 py-2 md:hidden">
          <span class="mr-2 font-display text-lg text-ink">Library</span>
          <router-link
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="shrink-0 rounded-md px-2.5 py-1.5 text-sm text-ink-muted"
            :class="(item.to === '/' ? $route.path === '/' : $route.path.startsWith(item.to)) && 'bg-paper font-medium !text-ink'"
          >
            {{ item.label }}
          </router-link>
        </nav>
        <main class="flex-1 overflow-y-auto">
          <div class="mx-auto w-full max-w-[1240px] px-5 sm:px-10">
            <router-view />
          </div>
        </main>
      </div>
    </div>
  </FrappeUIProvider>
</template>

<script setup>
import { FrappeUIProvider } from "frappe-ui"
import { ArrowLeftRight, BookOpen, LayoutDashboard, Users } from "lucide-vue-next"
import AppSidebar from "@/components/AppSidebar.vue"

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, to: "/" },
  { label: "Catalogue", icon: BookOpen, to: "/catalogue" },
  { label: "Members", icon: Users, to: "/members" },
  { label: "Transactions", icon: ArrowLeftRight, to: "/transactions" },
]
</script>
