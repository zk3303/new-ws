<template>
  <div class="carbon-page">
    <div class="page-header">
      <h1>碳足迹管理</h1>
      <p class="subtitle">智慧水务碳排放监测、分析与降碳管理</p>
    </div>

    <!-- 概览统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon carbon-icon">🌱</div>
        <div class="stat-content">
          <p class="stat-label">总碳排放（本月）</p>
          <h3 class="stat-value">{{ totalCarbon }} tCO₂</h3>
          <p class="stat-change down">↓ 8.2% 较上月</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon energy-icon">⚡</div>
        <div class="stat-content">
          <p class="stat-label">总能耗（本月）</p>
          <h3 class="stat-value">{{ totalEnergy }} MWh</h3>
          <p class="stat-change down">↓ 5.7% 较上月</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon water-icon">💧</div>
        <div class="stat-content">
          <p class="stat-label">总供水量（本月）</p>
          <h3 class="stat-value">{{ totalWater }} 万m³</h3>
          <p class="stat-change up">↑ 2.3% 较上月</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon intensity-icon">📊</div>
        <div class="stat-content">
          <p class="stat-label">碳排放强度</p>
          <h3 class="stat-value">{{ carbonIntensity }} kgCO₂/m³</h3>
          <p class="stat-change down">↓ 10.2% 较上月</p>
        </div>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label>时间范围</label>
        <el-select v-model="timeRange" @change="loadData">
          <el-option label="近7天" :value="7" />
          <el-option label="近30天" :value="30" />
          <el-option label="近90天" :value="90" />
        </el-select>
      </div>
      <div class="filter-group">
        <label>泵站</label>
        <el-select v-model="selectedStation" @change="loadData" placeholder="全部泵站">
          <el-option label="全部泵站" :value="null" />
          <el-option 
            v-for="station in stations" 
            :key="station.id" 
            :label="station.name" 
            :value="station.id" 
          />
        </el-select>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 碳排放趋势图 -->
      <div class="chart-card large">
        <div class="card-header">
          <h3>碳排放趋势</h3>
          <span class="card-subtitle">按日统计</span>
        </div>
        <div class="chart-content">
          <canvas ref="trendChart" height="300"></canvas>
        </div>
      </div>

      <!-- 碳排放构成 -->
      <div class="chart-card">
        <div class="card-header">
          <h3>碳排放构成</h3>
          <span class="card-subtitle">各类排放占比</span>
        </div>
        <div class="chart-content">
          <canvas ref="pieChart" height="250"></canvas>
        </div>
      </div>
    </div>

    <!-- 泵站碳排放排名 -->
    <div class="ranking-section">
      <div class="section-header">
        <h3>泵站碳排放排名</h3>
        <span class="section-subtitle">按总碳排放量排序</span>
      </div>
      
      <div class="ranking-table">
        <el-table :data="stationRanking" stripe>
          <el-table-column prop="rank" label="排名" width="80" align="center">
            <template #default="scope">
              <span class="rank-badge" :class="`rank-${scope.row.rank}`">
                {{ scope.row.rank }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="station_id" label="泵站ID" width="100" />
          <el-table-column prop="station_name" label="泵站名称" min-width="150" />
          <el-table-column prop="total_emissions" label="总碳排放 (tCO₂)" width="150" align="right">
            <template #default="scope">
              <span class="high-emission" v-if="scope.row.rank <= 3">
                {{ scope.row.total_emissions.toFixed(4) }}
              </span>
              <span v-else>{{ scope.row.total_emissions.toFixed(4) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="energy_kwh" label="能耗 (kWh)" width="120" align="right" />
          <el-table-column prop="water_m3" label="供水量 (m³)" width="120" align="right" />
          <el-table-column prop="emission_intensity" label="碳排放强度 (tCO₂/m³)" width="180" align="right">
            <template #default="scope">
              <span :class="scope.row.emission_intensity > 0.0001 ? 'warning' : 'normal'">
                {{ scope.row.emission_intensity.toFixed(6) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="center">
            <template #default="scope">
              <el-button type="primary" link @click="viewDetail(scope.row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 降碳潜力分析 -->
    <div class="reduction-section">
      <div class="section-header">
        <h3>降碳潜力分析</h3>
        <span class="section-subtitle">优化建议与收益测算</span>
      </div>
      
      <div class="reduction-cards">
        <div class="reduction-card" v-for="item in reductionData" :key="item.station_id">
          <div class="reduction-header">
            <h4>{{ item.station_name }}</h4>
            <span class="potential-badge">可降碳 {{ (item.potential_reduction_rate * 100).toFixed(0) }}%</span>
          </div>
          <div class="reduction-stats">
            <div class="stat-item">
              <p class="stat-label">当前碳排放</p>
              <p class="stat-value">{{ item.current_total_emissions.toFixed(4) }} tCO₂/月</p>
            </div>
            <div class="stat-item">
              <p class="stat-label">年降碳潜力</p>
              <p class="stat-value green">{{ item.annual_reduction_potential.toFixed(2) }} tCO₂</p>
            </div>
            <div class="stat-item">
              <p class="stat-label">年节约成本</p>
              <p class="stat-value green">¥ {{ item.annual_cost_saving.toFixed(2) }}</p>
            </div>
          </div>
          <div class="recommendation">
            <span class="label">优化建议：</span>
            <p>{{ item.recommendation }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import Chart from 'chart.js/auto'
import axios from 'axios'

const timeRange = ref(30)
const selectedStation = ref(null)
const stations = ref([])
const totalCarbon = ref(0)
const totalEnergy = ref(0)
const totalWater = ref(0)
const carbonIntensity = ref(0)
const stationRanking = ref([])
const reductionData = ref([])

const trendChart = ref(null)
const pieChart = ref(null)
let trendChartInstance = null
let pieChartInstance = null

// 加载泵站列表
const loadStations = async () => {
  try {
    const res = await axios.get('/api/pumps')
    if (res.data.code === 200) {
      stations.value = res.data.data
    }
  } catch (e) {
    console.error('加载泵站列表失败', e)
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 模拟统计数据
    totalCarbon.value = 128.56
    totalEnergy.value = 220.2
    totalWater.value = 125.8
    carbonIntensity.value = 0.098
  } catch (e) {
    console.error('加载统计数据失败', e)
  }
}

// 加载趋势数据
const loadTrendData = async () => {
  try {
    const days = timeRange.value
    const data = []
    const labels = []
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      labels.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }))
      
      data.push({
        total: Math.random() * 5 + 3,
        energy: Math.random() * 4 + 2.5,
        water: Math.random() * 0.8 + 0.3
      })
    }

    if (trendChartInstance) {
      trendChartInstance.destroy()
    }

    await nextTick()
    const ctx = trendChart.value.getContext('2d')
    trendChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: '总碳排放 (tCO₂)',
            data: data.map(d => d.total),
            borderColor: '#36a2eb',
            backgroundColor: 'rgba(54, 162, 235, 0.1)',
            fill: true,
            tension: 0.4
          },
          {
            label: '能源排放 (tCO₂)',
            data: data.map(d => d.energy),
            borderColor: '#ff6384',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            fill: true,
            tension: 0.4
          },
          {
            label: '供水排放 (tCO₂)',
            data: data.map(d => d.water),
            borderColor: '#4bc0c0',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'tCO₂'
            }
          }
        }
      }
    })
  } catch (e) {
    console.error('加载趋势数据失败', e)
  }
}

// 加载饼图数据
const loadPieData = async () => {
  try {
    if (pieChartInstance) {
      pieChartInstance.destroy()
    }

    await nextTick()
    const ctx = pieChart.value.getContext('2d')
    pieChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['电力消耗', '供水处理', '化学品使用', '其他'],
        datasets: [{
          data: [75, 15, 8, 2],
          backgroundColor: [
            '#36a2eb',
            '#4bc0c0',
            '#ffce56',
            '#9966ff'
          ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
          }
        },
        cutout: '70%'
      }
    })
  } catch (e) {
    console.error('加载饼图数据失败', e)
  }
}

// 加载泵站排名
const loadRanking = async () => {
  try {
    // 模拟排名数据
    const data = []
    const stationNames = ['东区泵房', '西区泵房', '南区泵房', '北区泵房', '中心泵房']
    
    for (let i = 0; i < 5; i++) {
      const energy = Math.random() * 50000 + 20000
      const water = Math.random() * 100000 + 50000
      const emissions = (energy / 1000) * 0.5839 + water * 0.00025
      
      data.push({
        rank: i + 1,
        station_id: `PR00${i + 1}`,
        station_name: stationNames[i],
        total_emissions: emissions,
        energy_kwh: Math.round(energy),
        water_m3: Math.round(water),
        emission_intensity: emissions / water
      })
    }
    
    data.sort((a, b) => b.total_emissions - a.total_emissions)
    data.forEach((item, idx) => item.rank = idx + 1)
    
    stationRanking.value = data
  } catch (e) {
    console.error('加载排名数据失败', e)
  }
}

// 加载降碳潜力数据
const loadReductionData = async () => {
  try {
    // 模拟降碳潜力数据
    const stationNames = ['东区泵房', '西区泵房', '南区泵房', '北区泵房', '中心泵房']
    const data = []
    
    for (let i = 0; i < 3; i++) {
      const currentEmissions = Math.random() * 30 + 10
      const reductionRate = 0.1 + Math.random() * 0.1
      
      data.push({
        station_id: `PR00${i + 1}`,
        station_name: stationNames[i],
        current_total_emissions: currentEmissions,
        potential_reduction_rate: reductionRate,
        annual_reduction_potential: currentEmissions * reductionRate * 12,
        annual_cost_saving: currentEmissions * reductionRate * 12 * 50,
        recommendation: '建议进行泵组变频改造、管网漏损治理、优化调度策略，可实现15%以上的碳减排。'
      })
    }
    
    reductionData.value = data
  } catch (e) {
    console.error('加载降碳潜力数据失败', e)
  }
}

const loadData = async () => {
  await Promise.all([
    loadStats(),
    loadTrendData(),
    loadPieData(),
    loadRanking(),
    loadReductionData()
  ])
}

const viewDetail = (row) => {
  ElMessage.info(`查看 ${row.station_name} 的碳足迹详情`)
  // 后续可以跳转到详情页或者弹出详情对话框
}

onMounted(async () => {
  await loadStations()
  await loadData()
})
</script>

<style scoped>
.carbon-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.subtitle {
  color: #64748b;
  margin: 0;
  font-size: 14px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-right: 16px;
}

.carbon-icon {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.energy-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.water-icon {
  background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
}

.intensity-icon {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.stat-content p {
  margin: 0;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.stat-change {
  font-size: 12px;
  font-weight: 500;
}

.stat-change.up {
  color: #ef4444;
}

.stat-change.down {
  color: #10b981;
}

/* 筛选栏 */
.filter-bar {
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  display: flex;
  gap: 24px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

/* 图表区域 */
.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.chart-card.large {
  grid-column: span 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.card-subtitle {
  font-size: 12px;
  color: #64748b;
}

.chart-content {
  position: relative;
}

/* 排名区域 */
.ranking-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.section-subtitle {
  font-size: 12px;
  color: #64748b;
}

.rank-badge {
  display: inline-block;
  width: 28px;
  height: 28px;
  line-height: 28px;
  text-align: center;
  border-radius: 50%;
  font-weight: 600;
  font-size: 13px;
}

.rank-1 {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.rank-2 {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  color: white;
}

.rank-3 {
  background: linear-gradient(135deg, #b45309 0%, #92400e 100%);
  color: white;
}

.high-emission {
  color: #ef4444;
  font-weight: 600;
}

.warning {
  color: #f59e0b;
  font-weight: 500;
}

.normal {
  color: #10b981;
}

/* 降碳潜力区域 */
.reduction-section {
  margin-bottom: 24px;
}

.reduction-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.reduction-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.reduction-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.reduction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.reduction-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.potential-badge {
  background: #dcfce7;
  color: #166534;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.reduction-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item p {
  margin: 0;
}

.stat-item .stat-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-item .stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.stat-item .stat-value.green {
  color: #10b981;
}

.recommendation {
  background: #f8fafc;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.6;
}

.recommendation .label {
  font-weight: 600;
  color: #374151;
}

.recommendation p {
  margin: 4px 0 0 0;
  color: #64748b;
}
</style>
