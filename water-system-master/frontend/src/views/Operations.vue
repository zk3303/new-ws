<template>
  <div class="operations">
    <!-- 统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">👷</div>
        <div class="stat-info">
          <div class="stat-value">{{ workers.length }}</div>
          <div class="stat-label">运维人员</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ freeWorkers }}</div>
          <div class="stat-label">空闲</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">🔄</div>
        <div class="stat-info">
          <div class="stat-value">{{ busyWorkers }}</div>
          <div class="stat-label">工作中</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">📋</div>
        <div class="stat-info">
          <div class="stat-value">{{ workorders.length }}</div>
          <div class="stat-label">工单总数</div>
        </div>
      </div>
    </div>

    <div class="content-grid">
      <!-- 运维人员列表 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">运维人员</span>
          <select class="select" v-model="workerFilter" @change="filterWorkers">
            <option value="">全部</option>
            <option value="free">空闲</option>
            <option value="busy">工作中</option>
          </select>
        </div>
        <div class="worker-list">
          <div 
            v-for="worker in filteredWorkers" 
            :key="worker.id"
            class="worker-card"
            :class="{ active: selectedWorker?.id === worker.id }"
            @click="selectWorker(worker)"
          >
            <div class="worker-avatar">{{ worker.avatar }}</div>
            <div class="worker-info">
              <div class="worker-name">{{ worker.name }}</div>
              <div class="worker-status" :class="worker.status">
                <span class="status-dot"></span>
                {{ worker.status_name }}
              </div>
            </div>
            <div class="worker-contact">
              <div class="phone">{{ worker.phone }}</div>
              <div class="skills">
                <span v-for="skill in worker.skills" :key="skill" class="skill-tag">{{ skill }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 工单列表 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">工单列表</span>
        </div>
        <div class="workorder-list">
          <div 
            v-for="order in workorders" 
            :key="order.id"
            class="workorder-item"
          >
            <div class="workorder-header">
              <span class="workorder-id">{{ order.id }}</span>
              <span class="workorder-status" :class="order.status">{{ getOrderStatusText(order.status) }}</span>
            </div>
            <div class="workorder-content">
              <div class="workorder-title">{{ order.pump_name }} - {{ order.type }}</div>
              <div class="workorder-desc">{{ order.description }}</div>
            </div>
            <div class="workorder-footer">
              <span class="worker-name">👷 {{ order.worker_name }}</span>
              <span class="create-time">{{ order.create_time }}</span>
            </div>
          </div>
          <div v-if="workorders.length === 0" class="empty-state">
            <span>暂无工单</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 人员详情弹窗 -->
    <div class="modal-overlay" v-if="showWorkerDetail" @click="showWorkerDetail = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <span>{{ selectedWorker?.name }} - 详情</span>
          <button class="modal-close" @click="showWorkerDetail = false">×</button>
        </div>
        <div class="modal-body">
          <div class="worker-detail">
            <div class="detail-avatar">{{ selectedWorker?.avatar }}</div>
            <div class="detail-info">
              <div class="detail-name">{{ selectedWorker?.name }}</div>
              <div class="detail-status" :class="selectedWorker?.status">{{ selectedWorker?.status_name }}</div>
            </div>
          </div>
          
          <div class="detail-section">
            <div class="detail-title">联系方式</div>
            <div class="detail-row">
              <span class="detail-label">电话</span>
              <span class="detail-value">{{ selectedWorker?.phone }}</span>
            </div>
          </div>
          
          <div class="detail-section">
            <div class="detail-title">专业技能</div>
            <div class="skills-list">
              <span v-for="skill in selectedWorker?.skills" :key="skill" class="skill-tag large">{{ skill }}</span>
            </div>
          </div>
          
          <div class="detail-section" v-if="selectedWorker?.current_task">
            <div class="detail-title">当前任务</div>
            <div class="current-task">
              <span class="task-id">{{ selectedWorker?.current_task }}</span>
              <button class="btn btn-outline btn-sm" @click="viewTask">查看任务</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { workerAPI, workorderAPI } from '../api'

const router = useRouter()

const workers = ref([])
const workorders = ref([])
const workerFilter = ref('')
const selectedWorker = ref(null)
const showWorkerDetail = ref(false)

const filteredWorkers = computed(() => {
  if (!workerFilter.value) return workers.value
  return workers.value.filter(w => w.status === workerFilter.value)
})

const freeWorkers = computed(() => workers.value.filter(w => w.status === 'free').length)
const busyWorkers = computed(() => workers.value.filter(w => w.status === 'busy').length)

async function loadData() {
  try {
    const [workerRes, orderRes] = await Promise.all([
      workerAPI.getList(),
      workorderAPI.getList()
    ])
    if (workerRes.code === 200) {
      workers.value = workerRes.data
    }
    if (orderRes.code === 200) {
      workorders.value = orderRes.data
    }
  } catch (e) {
    console.error(e)
  }
}

function filterWorkers() {}

function selectWorker(worker) {
  selectedWorker.value = worker
  showWorkerDetail.value = true
}

function getOrderStatusText(status) {
  const map = { pending: '待处理', processing: '处理中', done: '已完成' }
  return map[status] || status
}

function viewTask() {
  if (selectedWorker.value?.current_task) {
    router.push(`/alarms?id=${selectedWorker.value.current_task}`)
    showWorkerDetail.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.operations {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-icon.blue { background: rgba(0, 168, 255, 0.15); }
.stat-icon.green { background: rgba(0, 255, 136, 0.15); }
.stat-icon.orange { background: rgba(255, 165, 2, 0.15); }
.stat-icon.purple { background: rgba(168, 85, 247, 0.15); }

.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: bold; }
.stat-label { font-size: 12px; color: var(--text-secondary); }

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 15px;
  font-weight: 500;
}

.select {
  padding: 6px 12px;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 12px;
}

.worker-list {
  padding: 12px;
  max-height: 500px;
  overflow-y: auto;
}

.worker-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.worker-card:hover {
  background: var(--bg-card-hover);
}

.worker-card.active {
  background: rgba(0, 168, 255, 0.1);
  border: 1px solid var(--primary);
}

.worker-avatar {
  width: 48px;
  height: 48px;
  background: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}

.worker-info {
  flex: 1;
}

.worker-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.worker-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.worker-status .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.worker-status.free { color: var(--success); }
.worker-status.free .status-dot { background: var(--success); }

.worker-status.busy { color: var(--warning); }
.worker-status.busy .status-dot { background: var(--warning); }

.worker-contact {
  text-align: right;
}

.phone {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.skills {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.skill-tag {
  padding: 2px 8px;
  background: var(--bg-dark);
  border-radius: 4px;
  font-size: 10px;
  color: var(--text-secondary);
}

.skill-tag.large {
  padding: 4px 12px;
  font-size: 12px;
}

/* 工单 */
.workorder-list {
  padding: 12px;
  max-height: 500px;
  overflow-y: auto;
}

.workorder-item {
  background: var(--bg-dark);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
}

.workorder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.workorder-id {
  font-size: 13px;
  font-weight: 500;
}

.workorder-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.workorder-status.pending { background: rgba(255, 165, 2, 0.15); color: var(--warning); }
.workorder-status.processing { background: rgba(0, 168, 255, 0.15); color: var(--primary); }
.workorder-status.done { background: rgba(0, 255, 136, 0.15); color: var(--success); }

.workorder-title {
  font-size: 13px;
  margin-bottom: 4px;
}

.workorder-desc {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.workorder-footer {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  width: 400px;
  max-width: 90%;
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 24px;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.worker-detail {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.detail-avatar {
  width: 64px;
  height: 64px;
  background: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
}

.detail-name {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 4px;
}

.detail-status {
  font-size: 13px;
}

.detail-status.free { color: var(--success); }
.detail-status.busy { color: var(--warning); }

.detail-section {
  margin-bottom: 16px;
}

.detail-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
}

.detail-label {
  color: var(--text-secondary);
  font-size: 13px;
}

.detail-value {
  font-size: 13px;
}

.skills-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.current-task {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-dark);
  padding: 12px;
  border-radius: 6px;
}

.task-id {
  font-size: 13px;
  font-weight: 500;
}

.btn-sm {
  padding: 4px 10px;
  font-size: 12px;
}
</style>
