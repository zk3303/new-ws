import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Monitor from '../views/Monitor.vue'
import Alarms from '../views/Alarms.vue'
import Devices from '../views/Devices.vue'
import Operations from '../views/Operations.vue'
import Carbon from '../views/Carbon.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/monitor', name: 'Monitor', component: Monitor },
  { path: '/monitor/:id', name: 'PumpDetail', component: Monitor },
  { path: '/alarms', name: 'Alarms', component: Alarms },
  { path: '/devices', name: 'Devices', component: Devices },
  { path: '/devices/:id', name: 'DeviceDetail', component: Devices },
  { path: '/operations', name: 'Operations', component: Operations },
  { path: '/carbon', name: 'Carbon', component: Carbon },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
