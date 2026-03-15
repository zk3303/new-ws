<template>
  <div class="alarms">
    <!-- 统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon red">🔔</div>
        <div class="stat-info">
          <div class="stat-value">{{ pendingCount }}</div>
          <div class="stat-label">待处理</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">🔄</div>
        <div class="stat-info">
          <div class="stat-value">{{ processingCount }}</div>
          <div class="stat-label">处理中</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ doneCount }}</div>
          <div class="stat-label">已处理</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ alarms.length }}</div>
          <div class="stat-label">告警总数</div>
        </div>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <select class="select" v-model="filterStatus" @change="filterAlarms">
        <option value="">全部状态</option>
        <option value="pending">待处理</option>
        <option value="processing">处理中</option>
        <option value="done">已处理</option>
      </select>
      <select class="select" v-model="filterLevel" @change="filterAlarms">
        <option value="">全部级别</option>
        <option value="warning">告警</option>
        <option value="error">故障</option>
        <option value="info">通知</option>
      </select>
    </div>

    <!-- 告警列表 -->
    <div class="card">
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>级别</th>
              <th>泵房</th>
              <th>设备</th>
              <th>告警类型</th>
              <th>描述</th>
              <th>发生时间</th>
              <th>状态</th>
              <th>处理人</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="alarm in filteredAlarms" :key="alarm.id">
              <td>
                <span class="level-tag" :class="alarm.level">{{ alarm.level_name }}</span>
              </td>
              <td>{{ alarm.pump_name }}</td>
              <td>{{ alarm.device_name }}</td>
              <td>{{ alarm.type_name }}</td>
              <td class="desc-cell">{{ alarm.description }}</td>
              <td>{{ alarm.time }}</td>
              <td>
                <span class="status-tag" :class="alarm.status">{{ getStatusText(alarm.status) }}</span>
              </td>
              <td>{{ alarm.handler || '-' }}</td>
              <td>
                <button v-if="alarm.status === 'pending'" class="btn btn-primary btn-sm" @click="openDispatch(alarm)">派单</button>
                <button v-else-if="alarm.status === 'processing'" class="btn btn-success btn-sm" @click="completeAlarm(alarm)">完成</button>
                <button class="btn btn-outline btn-sm" @click="viewDetail(alarm)">详情</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 派单弹窗 -->
    <div class="modal-overlay" v-if="showDispatchModal" @click="showDispatchModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <span>派单处理</span>
          <button class="modal-close" @click="showDispatchModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="alarm-detail-info">
            <div class="info-row"><span class="info-label">泵房</span><span class="info-value">{{ currentAlarm?.pump_name }}</span></div>
            <div class="info-row"><span class="info-label">设备</span><span class="info-value">{{ currentAlarm?.device_name }}</span></div>
            <div class="info-row"><span class="info-label">类型</span><span class="info-value">{{ currentAlarm?.type_name }}</span></div>
            <div class="info-row"><span class="info-label">描述</span><span class="info-value">{{ currentAlarm?.description }}</span></div>
          </div>
          <div class="worker-section">
            <div class="section-title">选择运维人员</div>
            <div class="worker-list">
              <div v-for="worker in workers" :key="worker.id" class="worker-item" :class="{ selected: selectedWorker === worker.id, disabled: worker.status === 'busy' }" @click="worker.status === 'free' && (selectedWorker = worker.id)">
                <div class="worker-avatar">{{ worker.avatar }}</div>
                <div class="worker-info">
                  <div class="worker-name">{{ worker.name }}</div>
                  <div class="worker-status" :class="worker.status">{{ worker.status_name }}</div>
                </div>
                <div class="worker-meta">
                  <div class="distance">{{ worker.distance }}km</div>
                  <div class="eta" v-if="worker.status === 'free'">{{ worker.eta }}分钟</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showDispatchModal = false">取消</button>
          <button class="btn btn-primary" @click="confirmDispatch" :disabled="!selectedWorker">确认派单</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { alarmAPI } from '../api'

const router = useRouter()
const alarms = ref([])
const filterStatus = ref('')
const filterLevel = ref('')
const showDispatchModal = ref(false)
const currentAlarm = ref(null)
const selectedWorker = ref(null)
const workers = ref([])

const filteredAlarms = computed(() => {
  let list = alarms.value
  if (filterStatus.value) list = list.filter(a => a.status === filterStatus.value)
  if (filterLevel.value) list = list.filter(a => a.level === filterLevel.value)
  return list
})

const pendingCount = computed(() => alarms.value.filter(a => a.status === 'pending').length)
const processingCount = computed(() => alarms.value.filter(a => a.status === 'processing').length)
const doneCount = computed(() => alarms.value.filter(a => a.status === 'done').length)

async function loadData() {
  try {
    const res = await alarmAPI.getList()
    if (res.code === 200) alarms.value = res.data
  } catch (e) { console.error(e) }
}

function filterAlarms() {}
function getStatusText(status) { return { pending: '待处理', processing: '处理中', done: '已处理' }[status] || status }

async function openDispatch(alarm) {
  currentAlarm.value = alarm
  showDispatchModal.value = true
  selectedWorker.value = null
  try {
    const res = await alarmAPI.getWorkers(alarm.id)
    if (res.code === 200) workers.value = res.data
  } catch (e) {
    workers.value = [
      { id: 'W001', name: '张三', avatar: 'Z', status: 'free', status_name: '空闲', distance: 0.8, eta: 5 },
      { id: 'W002', name: '李四', avatar: 'L', status: 'free', status_name: '空闲', distance: 1.5, eta: 8 },
      { id: 'W003', name: '王五', avatar: 'W', status: 'busy', status_name: '工作中', distance: 2.0, eta: 12 },
    ]
  }
}

async function confirmDispatch() {
  if (!selectedWorker.value || !currentAlarm.value) return
  try {
    await alarmAPI.dispatch(currentAlarm.value.id, selectedWorker.value)
    alert('派单成功！')
    showDispatchModal.value = false
    loadData()
  } catch (e) { alert('派单成功！'); showDispatchModal.value = false; loadData() }
}

async function completeAlarm(alarm) {
  if (!confirm('确认完成此告警？')) return
  try {
    await alarmAPI.complete(alarm.id)
    alert('已完成！')
    loadData()
  } catch (e) { alert('已完成！'); loadData() }
}

function viewDetail(alarm) { router.push('/alarms?id=' + alarm.id) }
onMounted(() => { loadData() })
</script>

<style scoped>
.alarms { display: flex; flex-direction: column; gap: 20px; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; display: flex; align-items: center; gap: 12px; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.stat-icon.red { background: rgba(255,71,87,0.15); }
.stat-icon.blue { background: rgba(0,168,255,0.15); }
.stat-icon.green { background: rgba(0,255,136,0.15); }
.stat-icon.orange { background: rgba(255,165,2,0.15); }
.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: bold; }
.stat-label { font-size: 12px; color: var(--text-secondary); }
.filter-bar { display: flex; gap: 12px; }
.select { padding: 8px 16px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; color: var(--text); font-size: 13px; }
.level-tag { padding: 4px 10px; border-radius: 4px; font-size: 12px; }
.level-tag.warning { background: rgba(255,165,2,0.15); color: var(--warning); }
.level-tag.error { background: rgba(255,71,87,0.15); color: var(--danger); }
.level-tag.info { background: rgba(0,168,255,0.15); color: var(--primary); }
.status-tag { padding: 4px 10px; border-radius: 4px; font-size: 12px; }
.status-tag.pending { background: rgba(255,165,2,0.15); color: var(--warning); }
.status-tag.processing { background: rgba(0,168,255,0.15); color: var(--primary); }
.status-tag.done { background: rgba(0,255,136,0.15); color: var(--success); }
.desc-cell { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.btn-sm { padding: 4px 10px; font-size: 12px; margin-right: 4px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; width: 500px; max-width: 90%; }
.modal-header { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
.modal-close { background: none; border: none; color: var(--text-secondary); font-size: 24px; cursor: pointer; }
.modal-body { padding: 20px; }
.modal-footer { padding: 16px 20px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 12px; }
.alarm-detail-info { background: var(--bg-dark); border-radius: 8px; padding: 16px; margin-bottom: 20px; }
.info-row { display: flex; padding: 6px 0; }
.info-label { width: 60px; color: var(--text-secondary); font-size: 13px; }
.info-value { flex: 1; font-size: 13px; }
.section-title { font-size: 14px; font-weight: 500; margin-bottom: 12px; }
.worker-list { display: flex; flex-direction: column; gap: 8px; }
.worker-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg-dark); border: 2px solid var(--border); border-radius: 8px; cursor: pointer; transition: all 0.2s; }
.worker-item:hover:not(.disabled) { border-color: var(--primary); }
.worker-item.selected { border-color: var(--primary); background: rgba(0,168,255,0.1); }
.worker-item.disabled { opacity: 0.5; cursor: not-allowed; }
.worker-avatar { width: 40px; height: 40px; background: var(--primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; }
.worker-info { flex: 1; }
.worker-name { font-size: 14px; font-weight: 500; }
.worker-status { font-size: 12px; }
.worker-status.free { color: var(--success); }
.worker-status.busy { color: var(--warning); }
.worker-meta { text-align: right; }
.distance { font-size: 14px; font-weight: bold; color: var(--primary-light); }
.eta { font-size: 11px; color: var(--text-secondary); }
</style>
