import { createApp } from 'vue'
// import 'bootstrap/dist/css/bootstrap.min.css'
// import 'bootstrap/dist/js/bootstrap.bundle.min.js'

import 'bootstrap-icons/font/bootstrap-icons.css'

import App from './App.vue'

const el = document.getElementById('netcontrol')
const agreement = el.getAttribute('agreement')

createApp(App, {
  agreement
}).mount(el)
