<template>
  <div class="devices">
    <!-- 统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">⚙️</div>
        <div class="stat-info">
          <div class="stat-value">{{ devices.length }}</div>
          <div class="stat-label">设备总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ runningCount }}</div>
          <div class="stat-label">运行中</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">⏸️</div>
        <div class="stat-info">
          <div class="stat-value">{{ standbyCount }}</div>
          <div class="stat-label">待机</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">❌</div>
        <div class="stat-info">
          <div class="stat-value">{{ errorCount }}</div>
          <div class="stat-label">故障</div>
        </div>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <input type="text" class="input" placeholder="搜索设备..." v-model="searchText" @input="filterDevices">
      <select class="select" v-model="filterPump" @change="filterDevices">
        <option value="">全部泵房</option>
        <option v-for="pump in pumps" :key="pump.id" :value="pump.id">{{ pump.name }}</option>
      </select>
      <select class="select" v-model="filterStatus" @change="filterDevices">
        <option value="">全部状态</option>
        <option value="running">运行中</option>
        <option value="standby">待机</option>
        <option value="maintenance">维护中</option>
        <option value="error">故障</option>
      </select>
    </div>

    <!-- 设备列表 -->
    <div class="card">
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>设备ID</th>
              <th>设备名称</th>
              <th>所属泵房</th>
              <th>设备类型</th>
              <th>型号</th>
              <th>功率(kW)</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="device in filteredDevices" :key="device.id">
              <td>{{ device.id }}</td>
              <td>{{ device.name }}</td>
              <td>{{ device.pump_name }}</td>
              <td>{{ device.type }}</td>
              <td>{{ device.model }}</td>
              <td>{{ device.power }}</td>
              <td>
                <span class="status-tag" :class="device.status">{{ getStatusText(device.status) }}</span>
              </td>
              <td>
                <button class="btn btn-outline btn-sm" @click="viewDetail(device)">详情</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 设备详情弹窗 -->
    <div class="modal-overlay" v-if="showDetail" @click="showDetail = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <span>{{ selectedDevice?.name }} - 详情</span>
          <button class="modal-close" @click="showDetail = false">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">设备ID</span>
              <span class="detail-value">{{ selectedDevice?.id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">设备名称</span>
              <span class="detail-value">{{ selectedDevice?.name }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">所属泵房</span>
              <span class="detail-value">{{ selectedDevice?.pump_name }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">设备类型</span>
              <span class="detail-value">{{ selectedDevice?.type }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">型号</span>
              <span class="detail-value">{{ selectedDevice?.model }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">功率</span>
              <span class="detail-value">{{ selectedDevice?.power }} kW</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">状态</span>
              <span class="detail-value status" :class="selectedDevice?.status">{{ getStatusText(selectedDevice?.status) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">安装日期</span>
              <span class="detail-value">{{ selectedDevice?.install_date }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showDetail = false">关闭</button>
          <button class="btn btn-primary" @click="createWorkOrder">创建工单</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { deviceAPI, pumpAPI } from '../api'

const devices = ref([])
const pumps = ref([])
const searchText = ref('')
const filterPump = ref('')
const filterStatus = ref('')
const showDetail = ref(false)
const selectedDevice = ref(null)

const filteredDevices = computed(() => {
  let list = devices.value
  if (searchText.value) {
    const text = searchText.value.toLowerCase()
    list = list.filter(d => 
      d.name.toLowerCase().includes(text) || 
      d.id.toLowerCase().includes(text) ||
      d.pump_name.toLowerCase().includes(text)
    )
  }
  if (filterPump.value) {
    list = list.filter(d => d.pump_id === filterPump.value)
  }
  if (filterStatus.value) {
    list = list.filter(d => d.status === filterStatus.value)
  }
  return list
})

const runningCount = computed(() => devices.value.filter(d => d.status === 'running').length)
const standbyCount = computed(() => devices.value.filter(d => d.status === 'standby').length)
const errorCount = computed(() => devices.value.filter(d => d.status === 'error' || d.status === 'maintenance').length)

async function loadData() {
  try {
    const [deviceRes, pumpRes] = await Promise.all([
      deviceAPI.getList(),
      pumpAPI.getList()
    ])
    if (deviceRes.code === 200) {
      devices.value = deviceRes.data
    }
    if (pumpRes.code === 200) {
      pumps.value = pumpRes.data
    }
  } catch (e) {
    console.error(e)
  }
}

function filterDevices() {}

function getStatusText(status) {
  const map = { 
    running: '运行中', 
    standby: '待机', 
    maintenance: '维护中',
    error: '故障' 
  }
  return map[status] || status
}

function viewDetail(device) {
  selectedDevice.value = device
  showDetail.value = true
}

function createWorkOrder() {
  alert('工单创建功能已集成到告警管理中，请从告警页面派单')
  showDetail.value = false
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.devices {
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
.stat-icon.red { background: rgba(255, 71, 87, 0.15); }

.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: bold; }
.stat-label { font-size: 12px; color: var(--text-secondary); }

.filter-bar {
  display: flex;
  gap: 12px;
}

.input, .select {
  padding: 8px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 13px;
}

.input {
  flex: 1;
  max-width: 300px;
}

.status-tag {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag.running { background: rgba(0, 255, 136, 0.15); color: var(--success); }
.status-tag.standby { background: rgba(255, 165, 2, 0.15); color: var(--warning); }
.status-tag.maintenance { background: rgba(168, 85, 247, 0.15); color: #a855f7; }
.status-tag.error { background: rgba(255, 71, 87, 0.15); color: var(--danger); }

.btn-sm {
  padding: 4px 10px;
  font-size: 12px;
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
  width: 500px;
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

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.detail-value {
  font-size: 14px;
}

.detail-value.status.running { color: var(--success); }
.detail-value.status.standby { color: var(--warning); }
.detail-value.status.maintenance { color: #a855f7; }
.detail-value.status.error { color: var(--danger); }
</style>
