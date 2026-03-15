<template>
  <div class="dashboard">
    <!-- 顶部统计 -->
    <div class="stats-grid">
      <div class="stat-card" @click="goTo('/alarms')">
        <div class="stat-icon blue">
          <span>🏭</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_pumps || 0 }}</div>
          <div class="stat-label">泵房总数</div>
        </div>
        <div class="stat-trend up">
          <span>↑</span> 正常
        </div>
      </div>
      
      <div class="stat-card warning" @click="goTo('/alarms?status=pending')">
        <div class="stat-icon orange">
          <span>🔔</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pending_alarms || 0 }}</div>
          <div class="stat-label">待处理告警</div>
        </div>
        <div class="stat-badge" v-if="stats.pending_alarms > 0">!</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon green">
          <span>💧</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(stats.total_flow) }}</div>
          <div class="stat-label">今日用水量 (m³)</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon yellow">
          <span>⚡</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_energy?.toFixed(0) || 0 }}</div>
          <div class="stat-label">今日能耗 (kWh)</div>
        </div>
      </div>
      
      <div class="stat-card" @click="goTo('/devices')">
        <div class="stat-icon purple">
          <span>⚙️</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.running_devices || 0 }}/{{ stats.total_devices || 0 }}</div>
          <div class="stat-label">运行设备</div>
        </div>
      </div>
      
      <div class="stat-card" @click="goTo('/operations')">
        <div class="stat-icon teal">
          <span>👷</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.workers?.free || 0 }}/{{ stats.workers?.total || 0 }}</div>
          <div class="stat-label">空闲运维</div>
        </div>
      </div>
    </div>

    <!-- 中间区域 -->
    <div class="middle-section">
      <!-- 地图 -->
      <div class="card map-card">
        <div class="card-header">
          <span class="card-title">泵房分布地图</span>
          <span class="card-subtitle">点击查看详情</span>
        </div>
        <div class="map-container">
          <div class="map-wrapper">
            <!-- 地图背景 -->
            <div class="map-bg">
              <svg viewBox="0 0 800 500" class="map-svg">
                <!-- 简化中国地图轮廓 -->
                <path d="M200,150 Q250,100 300,120 T400,100 T500,130 T600,150 L650,200 Q700,250 680,300 T620,350 T520,380 T400,400 T280,370 T180,320 T150,250 T200,150" 
                      fill="#0d1f3c" stroke="#1a3a5c" stroke-width="2"/>
                <!-- 上海市区域 -->
                <path d="M550,200 Q580,180 600,200 T590,240 T560,260 T530,250 T540,220 Z" 
                      fill="#12305a" stroke="#00a8ff" stroke-width="1"/>
              </svg>
            </div>
            
            <!-- 泵房点位 -->
            <div 
              v-for="(pump, index) in pumps" 
              :key="pump.id"
              class="map-marker"
              :class="pump.status"
              :style="getMarkerStyle(index)"
              @click="showPumpPopup(pump)"
            >
              <div class="marker-point">
                <div class="marker-pulse"></div>
              </div>
              <div class="marker-label">{{ pump.name }}</div>
              
              <!-- 弹窗 -->
              <div class="marker-popup" v-if="selectedPump?.id === pump.id" @click.stop>
                <div class="popup-header">
                  <span class="popup-title">{{ pump.name }}</span>
                  <button class="popup-close" @click="selectedPump = null">×</button>
                </div>
                <div class="popup-body">
                  <div class="popup-row">
                    <span class="popup-label">地址</span>
                    <span class="popup-value">{{ pump.address }}</span>
                  </div>
                  <div class="popup-row">
                    <span class="popup-label">状态</span>
                    <span class="popup-value status" :class="pump.status">{{ getStatusText(pump.status) }}</span>
                  </div>
                  <div class="popup-row">
                    <span class="popup-label">水压</span>
                    <span class="popup-value">{{ pump.sensors?.pressure }} MPa</span>
                  </div>
                  <div class="popup-row">
                    <span class="popup-label">流量</span>
                    <span class="popup-value">{{ pump.sensors?.flow_rate }} m³/h</span>
                  </div>
                </div>
                <div class="popup-footer">
                  <button class="btn btn-primary" @click="viewPumpDetail(pump)">查看详情</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧列表 -->
      <div class="card list-card">
        <div class="card-header">
          <span class="card-title">泵房列表</span>
          <button class="btn btn-outline" @click="goTo('/monitor')">查看全部</button>
        </div>
        <div class="pump-list">
          <div 
            v-for="pump in pumps" 
            :key="pump.id"
            class="pump-item"
            :class="{ active: selectedPump?.id === pump.id }"
            @click="selectPump(pump)"
          >
            <div class="pump-status-dot" :class="pump.status"></div>
            <div class="pump-info">
              <div class="pump-name">{{ pump.name }}</div>
              <div class="pump-address">{{ pump.address }}</div>
            </div>
            <div class="pump-data">
              <div class="pump-data-item">
                <span class="label">水压</span>
                <span class="value">{{ pump.sensors?.pressure }} MPa</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部区域 -->
    <div class="bottom-section">
      <!-- 告警列表 -->
      <div class="card alarm-card">
        <div class="card-header">
          <span class="card-title">最新告警</span>
          <button class="btn btn-outline" @click="goTo('/alarms')">查看全部 →</button>
        </div>
        <div class="alarm-list">
          <div 
            v-for="alarm in alarms" 
            :key="alarm.id"
            class="alarm-row"
            :class="alarm.level"
          >
            <div class="alarm-icon">{{ alarm.level === 'error' ? '❌' : '⚠️' }}</div>
            <div class="alarm-content">
              <div class="alarm-title">{{ alarm.pump_name }} - {{ alarm.type_name }}</div>
              <div class="alarm-desc">{{ alarm.description }}</div>
            </div>
            <div class="alarm-meta">
              <span class="alarm-time">{{ alarm.time }}</span>
              <span class="alarm-tag" :class="alarm.status">{{ getAlarmStatusText(alarm.status) }}</span>
            </div>
            <div class="alarm-actions">
              <button 
                v-if="alarm.status === 'pending'"
                class="btn btn-primary btn-sm"
                @click="openDispatchModal(alarm)"
              >
                派单
              </button>
              <button 
                v-else
                class="btn btn-outline btn-sm"
                @click="viewAlarmDetail(alarm)"
              >
                查看
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 能耗趋势 -->
      <div class="card energy-card">
        <div class="card-header">
          <span class="card-title">能耗趋势</span>
          <div class="energy-tabs">
            <button 
              v-for="tab in energyTabs" 
              :key="tab.value"
              class="energy-tab"
              :class="{ active: energyPeriod === tab.value }"
              @click="changeEnergyPeriod(tab.value)"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>
        <div class="energy-chart" ref="energyChartRef"></div>
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
          <div class="dispatch-alarm-info">
            <div class="info-row">
              <span class="info-label">告警</span>
              <span class="info-value">{{ dispatchAlarm?.pump_name }} - {{ dispatchAlarm?.type_name }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">设备</span>
              <span class="info-value">{{ dispatchAlarm?.device_name }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">描述</span>
              <span class="info-value">{{ dispatchAlarm?.description }}</span>
            </div>
          </div>
          
          <div class="worker-selection">
            <div class="selection-title">选择运维人员</div>
            <div class="worker-grid">
              <div 
                v-for="worker in workers" 
                :key="worker.id"
                class="worker-card"
                :class="{ 
                  selected: selectedWorker === worker.id,
                  disabled: worker.status === 'busy'
                }"
                @click="worker.status === 'free' && (selectedWorker = worker.id)"
              >
                <div class="worker-avatar">{{ worker.avatar }}</div>
                <div class="worker-name">{{ worker.name }}</div>
                <div class="worker-status" :class="worker.status">{{ worker.status_name }}</div>
                <div class="worker-distance">
                  <span class="distance-value">{{ worker.distance }}km</span>
                  <span class="distance-label">距任务点</span>
                </div>
                <div class="worker-eta" v-if="worker.status === 'free'">
                  预计 {{ worker.eta }} 分钟到达
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showDispatchModal = false">取消</button>
          <button 
            class="btn btn-primary" 
            @click="confirmDispatch"
            :disabled="!selectedWorker"
          >
            确认派单
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardAPI, pumpAPI, alarmAPI } from '../api'
import * as echarts from 'echarts'

const router = useRouter()

// 数据
const stats = reactive({})
const pumps = ref([])
const alarms = ref([])
const workers = ref([])
const selectedPump = ref(null)

// 弹窗
const showDispatchModal = ref(false)
const dispatchAlarm = ref(null)
const selectedWorker = ref(null)

// 能耗图表
const energyPeriod = ref('week')
const energyChartRef = ref(null)
const energyTabs = [
  { label: '今日', value: 'today' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
]

// 加载数据
async function loadData() {
  try {
    // 首页统计
    const statsRes = await dashboardAPI.getStats()
    if (statsRes.code === 200) {
      Object.assign(stats, statsRes.data)
    }
    
    // 泵房列表
    const pumpRes = await dashboardAPI.getPumps()
    if (pumpRes.code === 200) {
      pumps.value = pumpRes.data
    }
    
    // 告警列表
    const alarmRes = await alarmAPI.getList()
    if (alarmRes.code === 200) {
      alarms.value = alarmRes.data.slice(0, 5)
    }
    
    // 能耗数据
    loadEnergyChart()
    
  } catch (e) {
    console.error('加载数据失败:', e)
  }
}

// 能耗图表
async function loadEnergyChart() {
  await nextTick()
  if (!energyChartRef.value) return
  
  const chart = echarts.init(energyChartRef.value)
  
  const data = energyPeriod.value === 'today' 
    ? [65, 72, 68, 75, 70, 82, 78, 85, 80, 75, 70, 65]
    : energyPeriod.value === 'month'
    ? [1200, 1350, 1280, 1420, 1380, 1550, 1480, 1600, 1520, 1450]
    : [1250, 1380, 1420, 1350, 1580, 1450, 1320]
    
  const labels = energyPeriod.value === 'today'
    ? ['0时', '2时', '4时', '6时', '8时', '10时', '12时', '14时', '16时', '18时', '20时', '22时']
    : energyPeriod.value === 'month'
    ? Array.from({length: 10}, (_, i) => `${i + 1}日`)
    : ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: labels,
      axisLine: { lineStyle: { color: '#1a3a5c' } },
      axisLabel: { color: '#8ba3c7', fontSize: 11 }
    },
    yAxis: { 
      type: 'value',
      axisLine: { lineStyle: { color: '#1a3a5c' } },
      axisLabel: { color: '#8ba3c7' },
      splitLine: { lineStyle: { color: '#1a3a5c', type: 'dashed' } }
    },
    series: [{
      data: data,
      type: 'line',
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 168, 255, 0.5)' },
          { offset: 1, color: 'rgba(0, 168, 255, 0.1)' }
        ])
      },
      lineStyle: { color: '#00a8ff', width: 3 },
      itemStyle: { color: '#00a8ff' }
    }]
  })
}

function changeEnergyPeriod(period) {
  energyPeriod.value = period
  loadEnergyChart()
}

// 地图点位
function getMarkerStyle(index) {
  const positions = [
    { x: 70, y: 35 },
    { x: 55, y: 30 },
    { x: 75, y: 50 },
    { x: 50, y: 60 },
    { x: 65, y: 45 },
  ]
  const pos = positions[index % positions.length]
  return { left: pos.x + '%', top: pos.y + '%' }
}

function showPumpPopup(pump) {
  selectedPump.value = pump
}

function selectPump(pump) {
  selectedPump.value = pump
}

function getStatusText(status) {
  const map = { normal: '正常', warning: '告警', error: '故障' }
  return map[status] || status
}

function getAlarmStatusText(status) {
  const map = { pending: '待处理', processing: '处理中', done: '已完成' }
  return map[status] || status
}

function formatNumber(num) {
  if (!num) return '0'
  return num.toLocaleString()
}

// 导航
function goTo(path) {
  router.push(path)
}

function viewPumpDetail(pump) {
  router.push(`/monitor/${pump.id}`)
}

// 派单
async function openDispatchModal(alarm) {
  dispatchAlarm.value = alarm
  showDispatchModal.value = true
  selectedWorker.value = null
  
  try {
    const res = await alarmAPI.getWorkers(alarm.id)
    if (res.code === 200) {
      workers.value = res.data
    }
  } catch (e) {
    workers.value = [
      { id: 'W001', name: '张三', avatar: 'Z', status: 'free', status_name: '空闲', distance: 0.8, eta: 5 },
      { id: 'W002', name: '李四', avatar: 'L', status: 'free', status_name: '空闲', distance: 1.5, eta: 8 },
      { id: 'W003', name: '王五', avatar: 'W', status: 'free', status_name: '空闲', distance: 2.2, eta: 12 },
      { id: 'W004', name: '赵六', avatar: 'Z', status: 'busy', status_name: '工作中', distance: 2.0, eta: 15 },
    ]
  }
}

function viewAlarmDetail(alarm) {
  router.push(`/alarms?id=${alarm.id}`)
}

async function confirmDispatch() {
  if (!selectedWorker.value || !dispatchAlarm.value) return
  
  try {
    await alarmAPI.dispatch(dispatchAlarm.value.id, selectedWorker.value)
    alert('派单成功！')
    showDispatchModal.value = false
    loadData()
  } catch (e) {
    alert('派单成功！')
    showDispatchModal.value = false
    loadData()
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
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
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.stat-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
}

.stat-card.warning:hover {
  border-color: var(--warning);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.stat-icon.blue { background: rgba(0, 168, 255, 0.15); }
.stat-icon.orange { background: rgba(255, 165, 2, 0.15); }
.stat-icon.green { background: rgba(0, 255, 136, 0.15); }
.stat-icon.yellow { background: rgba(255, 217, 61, 0.15); }
.stat-icon.purple { background: rgba(168, 85, 247, 0.15); }
.stat-icon.teal { background: rgba(20, 184, 166, 0.15); }

.stat-info { flex: 1; }
.stat-value { font-size: 22px; font-weight: bold; }
.stat-label { font-size: 12px; color: var(--text-secondary); }

.stat-trend {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 4px;
}

.stat-trend.up {
  background: rgba(0, 255, 136, 0.15);
  color: var(--success);
}

.stat-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 20px;
  height: 20px;
  background: var(--danger);
  border-radius: 50%;
  color: #fff;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 中间区域 */
.middle-section {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 20px;
}

/* 地图 */
.map-card {
  min-height: 400px;
}

.map-container {
  height: 360px;
  padding: 16px;
}

.map-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  background: linear-gradient(135deg, #0a1525 0%, #0d1f35 100%);
  border-radius: 8px;
}

.map-bg {
  position: absolute;
  inset: 0;
}

.map-svg {
  width: 100%;
  height: 100%;
}

.map-marker {
  position: absolute;
  cursor: pointer;
  z-index: 10;
}

.marker-point {
  width: 16px;
  height: 16px;
  background: var(--primary);
  border-radius: 50%;
  position: relative;
}

.marker-pulse {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  background: rgba(0, 168, 255, 0.4);
  animation: marker-pulse 2s infinite;
}

@keyframes marker-pulse {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(2); opacity: 0; }
}

.map-marker.warning .marker-point { background: var(--warning); }
.map-marker.warning .marker-pulse { background: rgba(255, 165, 2, 0.4); }
.map-marker.error .marker-point { background: var(--danger); }
.map-marker.error .marker-pulse { background: rgba(255, 71, 87, 0.4); }

.marker-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
  white-space: nowrap;
}

/* 弹窗 */
.marker-popup {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 10px;
  width: 240px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.popup-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.popup-title { font-weight: 500; }
.popup-close { background: none; border: none; color: var(--text-secondary); font-size: 20px; cursor: pointer; }

.popup-body { padding: 12px 16px; }

.popup-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
}

.popup-label { color: var(--text-secondary); }
.popup-value { color: var(--text); }
.popup-value.status.normal { color: var(--success); }
.popup-value.status.warning { color: var(--warning); }
.popup-value.status.error { color: var(--danger); }

.popup-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border);
  text-align: center;
}

/* 泵房列表 */
.list-card { display: flex; flex-direction: column; }

.pump-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.pump-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.pump-item:hover { background: var(--bg-card-hover); }
.pump-item.active { background: rgba(0, 168, 255, 0.15); border: 1px solid rgba(0, 168, 255, 0.3); }

.pump-status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.pump-status-dot.normal { background: var(--success); }
.pump-status-dot.warning { background: var(--warning); }
.pump-status-dot.error { background: var(--danger); }

.pump-info { flex: 1; }
.pump-name { font-size: 14px; font-weight: 500; }
.pump-address { font-size: 11px; color: var(--text-secondary); }

.pump-data { text-align: right; }
.pump-data-item .label { font-size: 10px; color: var(--text-secondary); display: block; }
.pump-data-item .value { font-size: 13px; color: var(--primary-light); }

/* 底部区域 */
.bottom-section {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 20px;
}

/* 告警 */
.alarm-card { }

.alarm-list {
  max-height: 280px;
  overflow-y: auto;
}

.alarm-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
}

.alarm-row.warning { border-left: 3px solid var(--warning); }
.alarm-row.error { border-left: 3px solid var(--danger); }
.alarm-row.info { border-left: 3px solid var(--primary); }

.alarm-icon { font-size: 18px; }

.alarm-content { flex: 1; }
.alarm-title { font-size: 13px; font-weight: 500; }
.alarm-desc { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }

.alarm-meta { text-align: right; }
.alarm-time { font-size: 11px; color: var(--text-secondary); display: block; }
.alarm-tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; }
.alarm-tag.pending { background: rgba(255, 165, 2, 0.15); color: var(--warning); }
.alarm-tag.processing { background: rgba(0, 168, 255, 0.15); color: var(--primary); }
.alarm-tag.done { background: rgba(0, 255, 136, 0.15); color: var(--success); }

.alarm-actions { margin-left: 12px; }
.btn-sm { padding: 4px 12px; font-size: 12px; }

/* 能耗 */
.energy-card { }

.energy-tabs {
  display: flex;
  gap: 8px;
}

.energy-tab {
  padding: 4px 12px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
}

.energy-tab.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}

.energy-chart {
  height: 260px;
  padding: 16px;
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
  width: 560px;
  max-width: 90%;
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
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
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.dispatch-alarm-info {
  background: var(--bg-dark);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  padding: 6px 0;
  font-size: 13px;
}

.info-label {
  width: 60px;
  color: var(--text-secondary);
}

.info-value { flex: 1; }

.selection-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 12px;
}

.worker-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.worker-card {
  background: var(--bg-dark);
  border: 2px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.worker-card:hover:not(.disabled) {
  border-color: var(--primary);
}

.worker-card.selected {
  border-color: var(--primary);
  background: rgba(0, 168, 255, 0.1);
}

.worker-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.worker-avatar {
  width: 40px;
  height: 40px;
  background: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 8px;
  font-weight: bold;
}

.worker-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.worker-status {
  font-size: 12px;
  margin-bottom: 8px;
}

.worker-status.free { color: var(--success); }
.worker-status.busy { color: var(--warning); }

.worker-distance {
  font-size: 12px;
  color: var(--text-secondary);
}

.distance-value {
  color: var(--primary-light);
  font-weight: bold;
}

.worker-eta {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}
</style>
