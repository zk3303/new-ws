<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo">
        <span class="logo-icon">💧</span>
        <span class="logo-text">智慧水务</span>
      </div>
      
      <nav class="nav">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-text">{{ item.name }}</span>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
        </router-link>
      </nav>
      
      <div class="sidebar-footer">
        <div class="user-info">
          <span class="user-avatar">👤</span>
          <span class="user-name">管理员</span>
        </div>
        <div class="version">v2.0.0</div>
      </div>
    </aside>

    <!-- 主内容 -->
    <main class="main">
      <header class="header">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="header-right">
          <div class="time">{{ currentTime }}</div>
          <div class="status-indicator">
            <span class="status-dot"></span>
            <span>系统正常</span>
          </div>
        </div>
      </header>
      
      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentTime = ref('')
let timer = null

const menuItems = computed(() => [
  { path: '/dashboard', name: '首页大屏', icon: '📊' },
  { path: '/monitor', name: '实时监控', icon: '📈' },
  { path: '/alarms', name: '告警管理', icon: '🔔' },
  { path: '/devices', name: '设备管理', icon: '⚙️' },
  { path: '/operations', name: '运维中心', icon: '👷' },
  { path: '/carbon', name: '碳足迹', icon: '🌱' },
])

const pageTitle = computed(() => {
  const item = menuItems.value.find(m => route.path.startsWith(m.path))
  return item ? item.name : '智慧水务'
})

const isActive = (path) => {
  if (path === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(path)
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-dark);
}

/* 侧边栏 */
.sidebar {
  width: 220px;
  background: linear-gradient(180deg, #0d1f3c 0%, #081420 100%);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 100;
}

.logo {
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--border);
}

.logo-icon {
  font-size: 32px;
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(135deg, #00a8ff, #00ff88);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s;
  position: relative;
}

.nav-item:hover {
  background: rgba(0, 168, 255, 0.1);
  color: var(--text);
}

.nav-item.active {
  background: linear-gradient(90deg, rgba(0, 168, 255, 0.2) 0%, transparent 100%);
  color: var(--primary);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--primary);
  border-radius: 0 2px 2px 0;
}

.nav-icon {
  font-size: 18px;
}

.nav-text {
  font-size: 14px;
}

.nav-badge {
  margin-left: auto;
  background: var(--danger);
  color: #fff;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.user-avatar {
  font-size: 20px;
}

.user-name {
  font-size: 13px;
  color: var(--text-secondary);
}

.version {
  font-size: 11px;
  color: var(--text-secondary);
  opacity: 0.6;
}

/* 主内容 */
.main {
  flex: 1;
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  height: 64px;
  background: rgba(13, 31, 60, 0.8);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(10px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.time {
  font-size: 13px;
  color: var(--text-secondary);
  font-family: monospace;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--success);
}

.status-dot {
  width: 8px;
  height: 8px;
  background: var(--success);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>
