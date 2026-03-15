<template>
  <div class="monitor">
    <!-- 统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">🏭</div>
        <div class="stat-info">
          <div class="stat-value">{{ pumps.length }}</div>
          <div class="stat-label">泵房总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ runningPumps }}</div>
          <div class="stat-label">正常运行</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">⚠️</div>
        <div class="stat-info">
          <div class="stat-value">{{ warningPumps }}</div>
          <div class="stat-label">告警</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">❌</div>
        <div class="stat-info">
          <div class="stat-value">{{ errorPumps }}</div>
          <div class="stat-label">故障</div>
        </div>
      </div>
    </div>

    <!-- 泵房列表 -->
    <div class="pump-grid">
      <div 
        v-for="pump in pumps" 
        :key="pump.id"
        class="pump-card"
        :class="{ active: selectedPump?.id === pump.id }"
        @click="selectPump(pump)"
      >
        <div class="pump-header">
          <div class="pump-title">
            <span class="pump-name">{{ pump.name }}</span>
            <span class="pump-id">{{ pump.id }}</span>
          </div>
          <span class="pump-status" :class="pump.status">{{ getStatusText(pump.status) }}</span>
        </div>
        
        <div class="pump-address">{{ pump.address }}</div>
        
        <div class="sensor-grid">
          <div class="sensor-item">
            <span class="sensor-icon">🌡️</span>
            <div class="sensor-value">{{ pump.sensors?.pressure }}</div>
            <div class="sensor-unit">MPa</div>
            <div class="sensor-label">水压</div>
          </div>
          <div class="sensor-item">
            <span class="sensor-icon">📊</span>
            <div class="sensor-value">{{ pump.sensors?.water_level }}</div>
            <div class="sensor-unit">m</div>
            <div class="sensor-label">水位</div>
          </div>
          <div class="sensor-item">
            <span class="sensor-icon">💧</span>
            <div class="sensor-value">{{ pump.sensors?.chlorine }}</div>
            <div class="sensor-unit">mg/L</div>
            <div class="sensor-label">余氯</div>
          </div>
          <div class="sensor-item">
            <span class="sensor-icon">🔄</span>
            <div class="sensor-value">{{ pump.sensors?.flow_rate }}</div>
            <div class="sensor-unit">m³/h</div>
            <div class="sensor-label">流量</div>
          </div>
          <div class="sensor-item">
            <span class="sensor-icon">⚡</span>
            <div class="sensor-value">{{ pump.sensors?.energy_consumption }}</div>
            <div class="sensor-unit">kWh</div>
            <div class="sensor-label">能耗</div>
          </div>
        </div>
        
        <div class="pump-footer">
          <span class="update-time">更新于 {{ currentTime }}</span>
          <button class="btn btn-primary btn-sm" @click.stop="viewDetail(pump)">查看详情 →</button>
        </div>
      </div>
    </div>

    <!-- 泵房详情弹窗 -->
    <div class="modal-overlay" v-if="showDetail" @click="showDetail = false">
      <div class="modal modal-lg" @click.stop>
        <div class="modal-header">
          <span>{{ selectedPump?.name }} - 详情</span>
          <button class="modal-close" @click="showDetail = false">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-section">
            <div class="detail-title">基本信息</div>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">泵房ID</span>
                <span class="detail-value">{{ selectedPump?.id }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">地址</span>
                <span class="detail-value">{{ selectedPump?.address }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">状态</span>
                <span class="detail-value status" :class="selectedPump?.status">{{ getStatusText(selectedPump?.status) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">容量</span>
                <span class="detail-value">{{ selectedPump?.capacity }} m³</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <div class="detail-title">实时数据</div>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">水压</span>
                <span class="detail-value highlight">{{ selectedPump?.sensors?.pressure }} MPa</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">水位</span>
                <span class="detail-value highlight">{{ selectedPump?.sensors?.water_level }} m</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">余氯</span>
                <span class="detail-value highlight">{{ selectedPump?.sensors?.chlorine }} mg/L</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">浊度</span>
                <span class="detail-value highlight">{{ selectedPump?.sensors?.turbidity }} NTU</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">流量</span>
                <span class="detail-value highlight">{{ selectedPump?.sensors?.flow_rate }} m³/h</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">能耗</span>
                <span class="detail-value highlight">{{ selectedPump?.sensors?.energy_consumption }} kWh</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <div class="detail-title">历史趋势</div>
            <div class="trend-chart" ref="trendChartRef"></div>
          </div>
          
          <div class="detail-section" v-if="selectedPump?.alarms?.length">
            <div class="detail-title">告警记录</div>
            <div class="alarm-mini-list">
              <div 
                v-for="alarm in selectedPump.alarms" 
                :key="alarm.id"
                class="alarm-mini-item"
                :class="alarm.level"
              >
                <span class="alarm-type">{{ alarm.type_name }}</span>
                <span class="alarm-status" :class="alarm.status">{{ getAlarmStatusText(alarm.status) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { pumpAPI } from '../api'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()

const pumps = ref([])
const selectedPump = ref(null)
const showDetail = ref(false)
const trendChartRef = ref(null)
const currentTime = new Date().toLocaleTimeString()

const runningPumps = computed(() => pumps.value.filter(p => p.status === 'normal').length)
const warningPumps = computed(() => pumps.value.filter(p => p.status === 'warning').length)
const errorPumps = computed(() => pumps.value.filter(p => p.status === 'error').length)

async function loadData() {
  try {
    const res = await pumpAPI.getList()
    if (res.code === 200) {
      pumps.value = res.data
      
      // 如果有路由参数，自动打开详情
      if (route.params.id) {
        const pump = pumps.value.find(p => p.id === route.params.id)
        if (pump) selectPump(pump)
      }
    }
  } catch (e) {
    console.error(e)
  }
}

function selectPump(pump) {
  selectedPump.value = pump
  showDetail.value = true
  loadTrendChart()
}

function viewDetail(pump) {
  router.push(`/monitor/${pump.id}`)
}

function getStatusText(status) {
  const map = { normal: '正常', warning: '告警', error: '故障' }
  return map[status] || status
}

function getAlarmStatusText(status) {
  const map = { pending: '待处理', processing: '处理中', done: '已处理' }
  return map[status] || status
}

async function loadTrendChart() {
  if (!selectedPump.value || !trendChartRef.value) return
  
  await nextTick()
  const chart = echarts.init(trendChartRef.value)
  
  const hours = []
  const pressureData = []
  const flowData = []
  
  for (let i = 23; i >= 0; i--) {
    const hour = new Date()
    hour.setHours(hour.getHours() - i)
    hours.push(hour.getHours() + '时')
    pressureData.push((0.35 + Math.random() * 0.2).toFixed(2))
    flowData.push((80 + Math.random() * 70).toFixed(0))
  }
  
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['水压', '流量'], textStyle: { color: '#8ba3c7' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: hours,
      axisLine: { lineStyle: { color: '#1a3a5c' } },
      axisLabel: { color: '#8ba3c7', fontSize: 10 }
    },
    yAxis: [
      { 
        type: 'value', 
        name: 'MPa',
        axisLine: { lineStyle: { color: '#1a3a5c' } },
        axisLabel: { color: '#8ba3c7' },
        splitLine: { lineStyle: { color: '#1a3a5c', type: 'dashed' } }
      },
      {
        type: 'value',
        name: 'm³/h',
        axisLine: { lineStyle: { color: '#1a3a5c' } },
        axisLabel: { color: '#8ba3c7' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '水压',
        type: 'line',
        data: pressureData,
        smooth: true,
        lineStyle: { color: '#00a8ff' },
        itemStyle: { color: '#00a8ff' }
      },
      {
        name: '流量',
        type: 'line',
        yAxisIndex: 1,
        data: flowData,
        smooth: true,
        lineStyle: { color: '#00ff88' },
        itemStyle: { color: '#00ff88' }
      }
    ]
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.monitor {
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

.pump-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.pump-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.pump-card:hover {
  border-color: var(--primary);
}

.pump-card.active {
  border-color: var(--primary);
  background: rgba(0, 168, 255, 0.05);
}

.pump-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.pump-title { }
.pump-name { font-size: 16px; font-weight: 500; display: block; }
.pump-id { font-size: 11px; color: var(--text-secondary); }

.pump-status {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.pump-status.normal { background: rgba(0, 255, 136, 0.15); color: var(--success); }
.pump-status.warning { background: rgba(255, 165, 2, 0.15); color: var(--warning); }
.pump-status.error { background: rgba(255, 71, 87, 0.15); color: var(--danger); }

.pump-address {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.sensor-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.sensor-item {
  background: var(--bg-dark);
  border-radius: 8px;
  padding: 10px 8px;
  text-align: center;
}

.sensor-icon {
  font-size: 16px;
  display: block;
  margin-bottom: 4px;
}

.sensor-value {
  font-size: 16px;
  font-weight: bold;
  color: var(--primary-light);
}

.sensor-unit {
  font-size: 10px;
  color: var(--text-secondary);
}

.sensor-label {
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.pump-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.update-time {
  font-size: 11px;
  color: var(--text-secondary);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

/* 弹窗 */
.modal-lg {
  width: 800px;
}

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
  max-height: 70vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.detail-label {
  color: var(--text-secondary);
  font-size: 13px;
}

.detail-value {
  font-size: 13px;
}

.detail-value.highlight {
  color: var(--primary-light);
  font-weight: bold;
}

.detail-value.status.normal { color: var(--success); }
.detail-value.status.warning { color: var(--warning); }
.detail-value.status.error { color: var(--danger); }

.trend-chart {
  height: 200px;
}

.alarm-mini-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.alarm-mini-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--bg-dark);
  border-radius: 6px;
  font-size: 12px;
}

.alarm-mini-item.warning { border-left: 3px solid var(--warning); }
.alarm-mini-item.error { border-left: 3px solid var(--danger); }

.alarm-status {
  font-size: 11px;
}

.alarm-status.pending { color: var(--warning); }
.alarm-status.processing { color: var(--primary); }
.alarm-status.done { color: var(--success); }
</style>
