import { createApp } from "vue"
import { Badge, Button, Dialog, FormControl, frappeRequest, resourcesPlugin, setConfig } from "frappe-ui"

import App from "./App.vue"
import router from "./router"
import "./index.css"

setConfig("resourceFetcher", frappeRequest)

const app = createApp(App)
app.use(router)
app.use(resourcesPlugin)
for (const [name, component] of Object.entries({ Badge, Button, Dialog, FormControl })) {
  app.component(name, component)
}
app.mount("#app")
