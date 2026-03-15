"""
智慧水务系统后端 - 完整版
"""

from fastapi import FastAPI, WebSocket, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import random
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from database import get_db
from carbon import CarbonCalculator

# ==================== 数据模型 ====================

# 泵房数据
PUMP_ROOMS = [
    {"id": "PR001", "name": "东区泵房", "address": "上海市浦东新区张江路100号", "lat": 31.2304, "lng": 121.4737, "capacity": 500, "install_date": "2020-01-15"},
    {"id": "PR002", "name": "西区泵房", "address": "上海市浦东新区金科路200号", "lat": 31.2204, "lng": 121.4637, "capacity": 400, "install_date": "2019-06-20"},
    {"id": "PR003", "name": "南区泵房", "address": "上海市浦东新区世纪大道300号", "lat": 31.2104, "lng": 121.4737, "capacity": 600, "install_date": "2021-03-10"},
    {"id": "PR004", "name": "北区泵房", "address": "上海市浦东新区龙阳路400号", "lat": 31.2404, "lng": 121.4637, "capacity": 450, "install_date": "2018-11-05"},
    {"id": "PR005", "name": "中心泵房", "address": "上海市浦东新区行政中心500号", "lat": 31.2254, "lng": 121.4687, "capacity": 800, "install_date": "2017-08-01"},
]

# 设备数据
DEVICES = []
for pump in PUMP_ROOMS:
    DEVICES.extend([
        {"id": f"{pump['id']}-P01", "name": "主水泵", "pump_id": pump["id"], "pump_name": pump["name"], "type": "水泵", "model": "CDL32-2", "status": "running", "power": 15, "install_date": pump["install_date"]},
        {"id": f"{pump['id']}-P02", "name": "备用泵", "pump_id": pump["id"], "pump_name": pump["name"], "type": "水泵", "model": "CDL32-2", "status": "standby", "power": 15, "install_date": pump["install_date"]},
        {"id": f"{pump['id']}-V01", "name": "变频器", "pump_id": pump["id"], "pump_name": pump["name"], "type": "变频器", "model": "ABB ACS510", "status": "running", "power": 5.5, "install_date": pump["install_date"]},
        {"id": f"{pump['id']}-C01", "name": "控制柜", "pump_id": pump["id"], "pump_name": pump["name"], "type": "控制柜", "model": "PKG-32", "status": "running", "power": 2.2, "install_date": pump["install_date"]},
    ])

# 告警数据
ALARMS = [
    {"id": "A001", "pump_id": "PR003", "pump_name": "南区泵房", "device_id": "PR003-P01", "device_name": "主水泵", "type": "pressure_high", "type_name": "水压偏高", "level": "warning", "level_name": "告警", "value": 0.58, "threshold": 0.55, "unit": "MPa", "time": "2026-03-11 18:45:30", "status": "pending", "description": "水压超过设定阈值0.55MPa"},
    {"id": "A002", "pump_id": "PR001", "pump_name": "东区泵房", "device_id": "PR001-C01", "device_name": "控制柜", "type": "chlorine_low", "type_name": "余氯偏低", "level": "warning", "level_name": "告警", "value": 0.25, "threshold": 0.30, "unit": "mg/L", "time": "2026-03-11 18:30:22", "status": "pending", "description": "余氯浓度低于标准"},
    {"id": "A003", "pump_id": "PR005", "pump_name": "中心泵房", "device_id": "PR005-P02", "device_name": "备用泵", "type": "vibration_high", "type_name": "振动异常", "level": "error", "level_name": "故障", "value": 8.5, "threshold": 5.0, "unit": "mm/s", "time": "2026-03-11 18:15:18", "status": "processing", "description": "水泵振动超过标准", "handler": "张三", "handle_time": "2026-03-11 18:20:00"},
    {"id": "A004", "pump_id": "PR002", "pump_name": "西区泵房", "device_id": "PR002-V01", "device_name": "变频器", "type": "temp_high", "type_name": "温度过高", "level": "error", "level_name": "故障", "value": 68, "threshold": 60, "unit": "℃", "time": "2026-03-11 17:55:10", "status": "pending", "description": "变频器温度超标"},
    {"id": "A005", "pump_id": "PR004", "pump_name": "北区泵房", "device_id": "PR004-P01", "device_name": "主水泵", "type": "maintenance", "type_name": "例行保养", "level": "info", "level_name": "保养", "value": 0, "threshold": 0, "unit": "", "time": "2026-03-11 17:30:00", "status": "done", "description": "已完成季度保养", "handler": "李四", "handle_time": "2026-03-11 17:45:00"},
]

# 运维人员
WORKERS = [
    {"id": "W001", "name": "张三", "phone": "13800138001", "avatar": "Z", "status": "busy", "status_name": "工作中", "lat": 31.2280, "lng": 121.4750, "distance": 0.8, "eta": 5, "current_task": "A003", "skills": ["水泵", "变频器"]},
    {"id": "W002", "name": "李四", "phone": "13800138002", "avatar": "L", "status": "free", "status_name": "空闲", "lat": 31.2350, "lng": 121.4680, "distance": 1.5, "eta": 8, "current_task": None, "skills": ["控制柜", "传感器"]},
    {"id": "W003", "name": "王五", "phone": "13800138003", "avatar": "W", "status": "free", "status_name": "空闲", "lat": 31.2180, "lng": 121.4800, "distance": 2.2, "eta": 12, "current_task": None, "skills": ["水泵", "控制柜"]},
    {"id": "W004", "name": "赵六", "phone": "13800138004", "avatar": "Z", "status": "busy", "status_name": "工作中", "lat": 31.2420, "lng": 121.4650, "distance": 2.0, "eta": 15, "current_task": "A004", "skills": ["变频器", "水泵"]},
    {"id": "W005", "name": "钱七", "phone": "13800138005", "avatar": "Q", "status": "free", "status_name": "空闲", "lat": 31.2100, "lng": 121.4700, "distance": 1.8, "eta": 10, "current_task": None, "skills": ["传感器", "控制柜"]},
]

# 工单
WORK_ORDERS = []

# 能耗数据
def generate_energy_data(days=7):
    data = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d")
        data.append({
            "date": date,
            "consumption": round(random.uniform(1200, 1800), 2),
            "cost": round(random.uniform(800, 1200), 2),
            "unit_price": 0.65
        })
    return data

# ==================== FastAPI ====================

app = FastAPI(title="智慧水务系统API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 生成实时传感器数据
def generate_sensor_data(pump_id):
    pump = next((p for p in PUMP_ROOMS if p["id"] == pump_id), None)
    if not pump:
        return None
    
    # 根据告警动态生成数据
    pump_alarms = [a for a in ALARMS if a["pump_id"] == pump_id and a["status"] != "done"]
    
    pressure = round(random.uniform(0.30, 0.50), 3)
    for alarm in pump_alarms:
        if alarm["type"] == "pressure_high":
            pressure = 0.58
        elif alarm["type"] == "chlorine_low":
            chlorine = 0.25
    
    chlorine = round(random.uniform(0.35, 0.45), 2)
    for alarm in pump_alarms:
        if alarm["type"] == "chlorine_low":
            chlorine = 0.25
    
    return {
        "pressure": pressure,
        "water_level": round(random.uniform(4.0, 7.0), 2),
        "chlorine": chlorine,
        "turbidity": round(random.uniform(0.2, 0.6), 2),
        "flow_rate": round(random.uniform(80, 150), 1),
        "temperature": round(random.uniform(25, 35), 1),
        "humidity": round(random.uniform(45, 65), 1),
        "vibration": round(random.uniform(1, 4), 2),
        "energy_consumption": round(random.uniform(20, 40), 2),
        "total_flow": round(random.uniform(30000, 50000), 0),
    }

# ==================== API 路由 ====================

@app.get("/")
async def root():
    return {"message": "智慧水务系统API", "version": "2.0.0", "docs": "/docs"}

# 获取首页统计数据
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    total_pumps = len(PUMP_ROOMS)
    online_pumps = total_pumps  # 模拟全在线
    
    pending_alarms = len([a for a in ALARMS if a["status"] == "pending"])
    processing_alarms = len([a for a in ALARMS if a["status"] == "processing"])
    
    # 计算总流量和总能耗
    total_flow = sum([generate_sensor_data(p["id"])["total_flow"] for p in PUMP_ROOMS])
    total_energy = sum([generate_sensor_data(p["id"])["energy_consumption"] for p in PUMP_ROOMS])
    
    # 设备统计
    total_devices = len(DEVICES)
    running_devices = len([d for d in DEVICES if d["status"] == "running"])
    standby_devices = len([d for d in DEVICES if d["status"] == "standby"])
    error_devices = len([d for d in DEVICES if d["status"] == "error"])
    
    return {
        "code": 200,
        "data": {
            "total_pumps": total_pumps,
            "online_pumps": online_pumps,
            "total_alarms": len(ALARMS),
            "pending_alarms": pending_alarms,
            "processing_alarms": processing_alarms,
            "total_flow": round(total_flow, 0),
            "total_energy": round(total_energy, 2),
            "total_devices": total_devices,
            "running_devices": running_devices,
            "standby_devices": standby_devices,
            "error_devices": error_devices,
            "workers": {
                "total": len(WORKERS),
                "free": len([w for w in WORKERS if w["status"] == "free"]),
                "busy": len([w for w in WORKERS if w["status"] == "busy"])
            }
        }
    }

# 获取泵房列表（带实时数据）
@app.get("/api/pumps")
async def get_pumps():
    pumps = []
    for pump in PUMP_ROOMS:
        sensors = generate_sensor_data(pump["id"])
        pump_alarms = [a for a in ALARMS if a["pump_id"] == pump["id"] and a["status"] != "done"]
        
        status = "normal"
        if any(a["level"] == "error" for a in pump_alarms):
            status = "error"
        elif any(a["level"] == "warning" for a in pump_alarms):
            status = "warning"
        
        pumps.append({
            **pump,
            "status": status,
            "sensors": sensors,
            "alarm_count": len(pump_alarms)
        })
    
    return {"code": 200, "data": pumps}

# 获取泵房详情
@app.get("/api/pump/{pump_id}")
async def get_pump_detail(pump_id: str):
    pump = next((p for p in PUMP_ROOMS if p["id"] == pump_id), None)
    if not pump:
        return {"code": 404, "message": "泵房不存在"}
    
    sensors = generate_sensor_data(pump_id)
    pump_devices = [d for d in DEVICES if d["pump_id"] == pump_id]
    pump_alarms = [a for a in ALARMS if a["pump_id"] == pump_id]
    
    return {
        "code": 200,
        "data": {
            **pump,
            "sensors": sensors,
            "devices": pump_devices,
            "alarms": pump_alarms
        }
    }

# 获取告警列表
@app.get("/api/alarms")
async def get_alarms(status: str = None, level: str = None):
    alarms = ALARMS
    if status and status != "all":
        alarms = [a for a in alarms if a["status"] == status]
    if level:
        alarms = [a for a in alarms if a["level"] == level]
    return {"code": 200, "data": alarms, "total": len(alarms)}

# 获取告警详情
@app.get("/api/alarm/{alarm_id}")
async def get_alarm_detail(alarm_id: str):
    alarm = next((a for a in ALARMS if a["id"] == alarm_id), None)
    if not alarm:
        return {"code": 404, "message": "告警不存在"}
    return {"code": 200, "data": alarm}

# 获取可派单的运维人员
@app.get("/api/alarm/{alarm_id}/workers")
async def get_available_workers(alarm_id: str):
    alarm = next((a for a in ALARMS if a["id"] == alarm_id), None)
    if not alarm:
        return {"code": 404, "message": "告警不存在"}
    
    # 模拟根据设备类型匹配人员
    device_type = alarm.get("device_name", "")
    available_workers = []
    
    for worker in WORKERS:
        # 随机生成距离和ETA
        worker["distance"] = round(random.uniform(0.5, 5.0), 1)
        worker["eta"] = int(worker["distance"] * 5)
        available_workers.append(worker)
    
    # 按距离排序
    available_workers.sort(key=lambda x: x["distance"])
    
    return {"code": 200, "data": available_workers}

# 派单
@app.post("/api/alarm/{alarm_id}/dispatch")
async def dispatch_alarm(alarm_id: str, worker_id: str):
    alarm = next((a for a in ALARMS if a["id"] == alarm_id), None)
    worker = next((w for w in WORKERS if w["id"] == worker_id), None)
    
    if not alarm or not worker:
        return {"code": 404, "message": "告警或人员不存在"}
    
    if worker["status"] == "busy":
        return {"code": 400, "message": "该人员正忙"}
    
    # 更新告警状态
    alarm["status"] = "processing"
    alarm["handler"] = worker["name"]
    alarm["dispatch_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 更新人员状态
    worker["status"] = "busy"
    worker["status_name"] = "工作中"
    worker["current_task"] = alarm_id
    
    # 创建工单
    work_order = {
        "id": f"WO{len(WORK_ORDERS) + 1:03d}",
        "alarm_id": alarm_id,
        "pump_id": alarm["pump_id"],
        "pump_name": alarm["pump_name"],
        "device_name": alarm["device_name"],
        "type": alarm["type_name"],
        "description": alarm["description"],
        "worker_id": worker_id,
        "worker_name": worker["name"],
        "status": "processing",
        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    WORK_ORDERS.append(work_order)
    
    return {"code": 200, "message": f"派单成功，已分配给 {worker["name"]}", "data": {"alarm": alarm, "worker": worker, "work_order": work_order}}

# 处理告警（完成工单）
@app.post("/api/alarm/{alarm_id}/complete")
async def complete_alarm(alarm_id: str):
    alarm = next((a for a in ALARMS if a["id"] == alarm_id), None)
    if not alarm:
        return {"code": 404, "message": "告警不存在"}
    
    alarm["status"] = "done"
    alarm["complete_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 释放人员
    for worker in WORKERS:
        if worker.get("current_task") == alarm_id:
            worker["status"] = "free"
            worker["status_name"] = "空闲"
            worker["current_task"] = None
    
    return {"code": 200, "message": "告警已处理完成", "data": alarm}

# 获取设备列表
@app.get("/api/devices")
async def get_devices(pump_id: str = None, status: str = None):
    devices = DEVICES
    if pump_id:
        devices = [d for d in devices if d["pump_id"] == pump_id]
    if status:
        devices = [d for d in devices if d["status"] == status]
    return {"code": 200, "data": devices}

# 获取设备详情
@app.get("/api/device/{device_id}")
async def get_device_detail(device_id: str):
    device = next((d for d in DEVICES if d["id"] == device_id), None)
    if not device:
        return {"code": 404, "message": "设备不存在"}
    return {"code": 200, "data": device}

# 获取运维人员列表
@app.get("/api/workers")
async def get_workers(status: str = None):
    workers = WORKERS
    if status:
        workers = [w for w in workers if w["status"] == status]
    return {"code": 200, "data": workers}

# 获取运维人员详情
@app.get("/api/worker/{worker_id}")
async def get_worker_detail(worker_id: str):
    worker = next((w for w in WORKERS if w["id"] == worker_id), None)
    if not worker:
        return {"code": 404, "message": "人员不存在"}
    return {"code": 200, "data": worker}

# 获取工单列表
@app.get("/api/workorders")
async def get_workorders(status: str = None):
    orders = WORK_ORDERS
    if status:
        orders = [o for o in orders if o["status"] == status]
    return {"code": 200, "data": orders}

# 获取能耗报表
@app.get("/api/energy")
async def get_energy_report(period: str = "week"):
    if period == "today":
        days = 1
    elif period == "month":
        days = 30
    else:
        days = 7
    
    data = generate_energy_data(days)
    total_consumption = sum([d["consumption"] for d in data])
    total_cost = sum([d["cost"] for d in data])
    
    return {
        "code": 200,
        "data": {
            "period": period,
            "days": days,
            "records": data,
            "total_consumption": round(total_consumption, 2),
            "total_cost": round(total_cost, 2),
            "avg_daily": round(total_consumption / days, 2)
        }
    }

# 获取历史趋势数据
@app.get("/api/trend/{pump_id}")
async def get_trend_data(pump_id: str, hours: int = 24):
    data = []
    for i in range(hours):
        time = datetime.now() - timedelta(hours=hours-i-1)
        sensors = generate_sensor_data(pump_id)
        data.append({
            "time": time.strftime("%H:%M"),
            "pressure": sensors["pressure"],
            "flow_rate": sensors["flow_rate"],
            "energy": sensors["energy_consumption"]
        })
    return {"code": 200, "data": data}

# ==================== 碳足迹API ====================

# 获取指定泵站的碳足迹数据
@app.get("/api/carbon/station/{station_id}")
async def get_station_carbon(station_id: int, days: int = 30, db: Session = Depends(get_db)):
    calculator = CarbonCalculator(db)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    data = calculator.get_station_emissions(station_id, start_time, end_time)
    return {"code": 200, "data": data}

# 获取所有泵站碳排放排名
@app.get("/api/carbon/ranking")
async def get_carbon_ranking(days: int = 30, db: Session = Depends(get_db)):
    calculator = CarbonCalculator(db)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    data = calculator.get_all_stations_emissions(start_time, end_time)
    return {"code": 200, "data": data}

# 获取碳足迹趋势数据
@app.get("/api/carbon/trend")
async def get_carbon_trend(station_id: int = None, days: int = 30, db: Session = Depends(get_db)):
    calculator = CarbonCalculator(db)
    data = calculator.get_trend_data(station_id, days)
    return {"code": 200, "data": data}

# 获取泵站降碳潜力分析
@app.get("/api/carbon/reduction/{station_id}")
async def get_carbon_reduction(station_id: int, db: Session = Depends(get_db)):
    calculator = CarbonCalculator(db)
    data = calculator.calculate_reduction_potential(station_id)
    return {"code": 200, "data": data}

# 手动计算碳排放
@app.post("/api/carbon/calculate")
async def calculate_carbon(energy_kwh: float, water_m3: float = 0, chemical_kg: float = 0, db: Session = Depends(get_db)):
    calculator = CarbonCalculator(db)
    data = calculator.calculate_emissions(energy_kwh, water_m3, chemical_kg)
    return {"code": 200, "data": data}

# ==================== WebSocket 实时推送 ====================

class RealtimePusher:
    def __init__(self):
        self.clients = []
        
    async def start(self):
        while True:
            # 生成实时数据
            for pump in PUMP_ROOMS:
                sensors = generate_sensor_data(pump["id"])
                data = {
                    "type": "realtime",
                    "pump_id": pump["id"],
                    "timestamp": datetime.now().isoformat(),
                    "sensors": sensors
                }
                await self.broadcast(data)
            await asyncio.sleep(3)
            
    async def broadcast(self, data):
        for client in self.clients:
            try:
                await client.send_json(data)
            except:
                pass

pusher = RealtimePusher()

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(pusher.start())
    yield

app.router.lifespan_context = lifespan

@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket):
    await websocket.accept()
    pusher.clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        if websocket in pusher.clients:
            pusher.clients.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
