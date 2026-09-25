import { createRouter, createWebHistory } from "vue-router"
import { isStaff } from "@/utils"

const staffRoutes = [
  { path: "/", name: "Dashboard", component: () => import("@/pages/Dashboard.vue") },
  { path: "/members", name: "Members", component: () => import("@/pages/Members.vue") },
  { path: "/transactions", name: "Transactions", component: () => import("@/pages/Transactions.vue") },
]

const studentRoutes = [{ path: "/", name: "MyLoans", component: () => import("@/pages/MyLoans.vue") }]

const routes = [
  ...(isStaff ? staffRoutes : studentRoutes),
  { path: "/catalogue", name: "Catalogue", component: () => import("@/pages/Catalogue.vue") },
  { path: "/:pathMatch(.*)*", redirect: "/" },
]

export default createRouter({ history: createWebHistory("/library"), routes })
