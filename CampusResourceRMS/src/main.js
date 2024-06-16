/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'
import router from './router'

import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css'

// Composables
import { createApp } from 'vue'

const app = createApp(App)

registerPlugins(app)

app.component('VueDatePicker', VueDatePicker);

app.use(router)

app.mount('#app')
