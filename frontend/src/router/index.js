import { createRouter, createWebHistory } from 'vue-router'

const routes = [

    {
    path: '/',
    name: 'OnuReg',
    component: () => import('@/views/OnuRegView.vue'),
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})

