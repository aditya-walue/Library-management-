import { dayjs } from "frappe-ui"

export function errorMessage(error) {
  const text = error?.messages?.[0] || error?.message || "Something went wrong"
  return text.replace(/<[^>]*>/g, "")
}

export function formatDate(value) {
  return value ? dayjs(value).format("D MMM YYYY") : "—"
}

export function relativeDue(value) {
  if (!value) return ""
  const days = dayjs(value).startOf("day").diff(dayjs().startOf("day"), "day")
  if (days === 0) return "Due today"
  if (days > 0) return `Due in ${days} day${days === 1 ? "" : "s"}`
  return `${-days} day${days === -1 ? "" : "s"} overdue`
}

export const categories = [
  "Fiction",
  "Non-Fiction",
  "Science",
  "Technology",
  "History",
  "Biography",
  "Children",
  "Reference",
  "Other",
]

export function initials(name = "") {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase()
}

export function greeting() {
  const h = dayjs().hour()
  return h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening"
}

export function hash(str = "") {
  let h = 2166136261
  for (let i = 0; i < str.length; i++) h = Math.imul(h ^ str.charCodeAt(i), 16777619)
  return (h >>> 0) / 4294967296
}

// One colour per category, reused for pills, icons and bars.
export const categoryColors = {
  Fiction: "#D9485F",
  "Non-Fiction": "#E07A2E",
  Science: "#2F6FE4",
  Technology: "#0F9F6E",
  History: "#B7791F",
  Biography: "#7C5CE0",
  Children: "#B98300",
  Reference: "#0E9AA7",
  Other: "#64748B",
}

export const colorFor = (category) => categoryColors[category] || categoryColors.Other
export const tintFor = (category, alpha = "1A") => colorFor(category) + alpha

export const formatFine = (amount) => Number(amount || 0).toLocaleString(undefined, { maximumFractionDigits: 2 })

// Librarians and System Managers manage the library; everyone else gets the student view.
export const isStaff = window.is_staff !== false

// QR labels carry a link, so any phone camera can open the title too.
export const articleQrValue = (name) =>
  `${window.location.origin}/library/catalogue?article=${encodeURIComponent(name)}`
