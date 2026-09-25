import { createRouter, createWebHistory } from "vue-router"

const routes = [
  { path: "/", name: "Dashboard", component: () => import("@/pages/Dashboard.vue") },
  { path: "/catalogue", name: "Catalogue", component: () => import("@/pages/Catalogue.vue") },
  { path: "/members", name: "Members", component: () => import("@/pages/Members.vue") },
  { path: "/transactions", name: "Transactions", component: () => import("@/pages/Transactions.vue") },
  { path: "/:pathMatch(.*)*", redirect: "/" },
]

export default createRouter({ history: createWebHistory("/library"), routes })
