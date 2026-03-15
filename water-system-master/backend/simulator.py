from datetime import datetime, timedelta
import random
import asyncio
from influxdb_client.client.write_api import SYNCHRONOUS
from config import settings
from database import influx_write_api, SessionLocal
from models import PumpStation, Device, Sensor

class DataSimulator:
    """模拟数据生成器"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.stations = []
        self._init_stations()
    
    def _init_stations(self):
        """初始化20个泵站的基础数据"""
        existing_stations = self.db.query(PumpStation).count()
        if existing_stations < settings.PUMP_COUNT:
            # 创建20个模拟泵站
            for i in range(settings.PUMP_COUNT):
                station = PumpStation(
                    name=f"第{i+1}供水泵站",
                    address=f"某市{random.choice(['东城区', '西城区', '南城区', '北城区', '高新区'])}大道{i+1}号",
                    latitude=39.9 + random.uniform(-0.5, 0.5),
                    longitude=116.3 + random.uniform(-0.5, 0.5),
                    capacity=random.uniform(100, 500),
                    installed_power=random.uniform(50, 200),
                    contact_person=f"张{i+1}工",
                    contact_phone=f"138{random.randint(10000000, 99999999)}",
                    description=f"设计供水能力{random.randint(10000, 50000)}m³/天，服务人口{random.randint(5000, 20000)}人"
                )
                self.db.add(station)
                self.db.flush()
                
                # 每个泵站添加3-5台设备
                device_count = random.randint(3, 5)
                for j in range(device_count):
                    device = Device(
                        station_id=station.id,
                        name=f"水泵{j+1}",
                        device_type="pump",
                        model=f"WP-{random.randint(100, 999)}",
                        serial_number=f"PUMP{station.id:03d}{j:03d}{random.randint(1000, 9999)}",
                        installation_date=datetime.utcnow() - timedelta(days=random.randint(30, 1000))
                    )
                    self.db.add(device)
                    self.db.flush()
                    
                    # 每个设备添加传感器
                    sensor_types = [
                        ("pressure", "MPa", 0.1, 0.6),
                        ("flow_rate", "m³/h", 0, 100),
                        ("temperature", "℃", 5, 40),
                        ("vibration", "mm/s", 0, 4.5),
                        ("active_power", "kW", 10, 100)
                    ]
                    
                    for st, unit, min_val, max_val in sensor_types:
                        sensor = Sensor(
                            device_id=device.id,
                            name=f"{st}传感器",
                            sensor_type=st,
                            unit=unit,
                            min_threshold=min_val,
                            max_threshold=max_val
                        )
                        self.db.add(sensor)
            
            self.db.commit()
        
        # 加载所有泵站
        self.stations = self.db.query(PumpStation).all()
        print(f"已加载 {len(self.stations)} 个泵站模拟数据")
    
    def generate_sensor_data(self, station_id: int, timestamp: datetime = None) -> list:
        """生成单个泵站的传感器模拟数据"""
        if not timestamp:
            timestamp = datetime.utcnow()
        
        # 基础参数带随机波动
        base_pressure = random.uniform(0.2, 0.5)
        base_flow = random.uniform(20, 80)
        base_temp = random.uniform(15, 30)
        base_vibration = random.uniform(0.5, 2.5)
        base_power = random.uniform(30, 80)
        
        # 10%概率生成异常数据
        is_abnormal = random.random() < 0.1
        
        points = []
        
        # 压力
        pressure = base_pressure + random.uniform(-0.05, 0.05)
        if is_abnormal and random.random() < 0.3:
            pressure = random.uniform(0.6, 0.8)  # 压力过高
        
        points.append({
            "measurement": "sensor_data",
            "tags": {
                "station_id": str(station_id),
                "sensor_type": "pressure",
                "unit": "MPa"
            },
            "fields": {
                "_value": round(pressure, 3)
            },
            "time": timestamp
        })
        
        # 流量
        flow = base_flow + random.uniform(-5, 5)
        if is_abnormal and random.random() < 0.2:
            flow = random.uniform(0, 10)  # 流量过低（可能漏损）
        
        points.append({
            "measurement": "sensor_data",
            "tags": {
                "station_id": str(station_id),
                "sensor_type": "flow_rate",
                "unit": "m³/h"
            },
            "fields": {
                "_value": round(flow, 2)
            },
            "time": timestamp
        })
        
        # 温度
        temp = base_temp + random.uniform(-2, 2)
        if is_abnormal and random.random() < 0.2:
            temp = random.uniform(40, 60)  # 温度过高
        
        points.append({
            "measurement": "sensor_data",
            "tags": {
                "station_id": str(station_id),
                "sensor_type": "temperature",
                "unit": "℃"
            },
            "fields": {
                "_value": round(temp, 1)
            },
            "time": timestamp
        })
        
        # 振动
        vibration = base_vibration + random.uniform(-0.2, 0.2)
        if is_abnormal and random.random() < 0.2:
            vibration = random.uniform(5, 10)  # 振动过大
        
        points.append({
            "measurement": "sensor_data",
            "tags": {
                "station_id": str(station_id),
                "sensor_type": "vibration",
                "unit": "mm/s"
            },
            "fields": {
                "_value": round(vibration, 2)
            },
            "time": timestamp
        })
        
        # 电功率
        power = base_power + random.uniform(-5, 5)
        if is_abnormal and random.random() < 0.2:
            power = random.uniform(100, 150)  # 功率过高
        
        points.append({
            "measurement": "sensor_data",
            "tags": {
                "station_id": str(station_id),
                "sensor_type": "active_power",
                "unit": "kW"
            },
            "fields": {
                "_value": round(power, 2)
            },
            "time": timestamp
        })
        
        # 水质相关
        points.extend([
            {
                "measurement": "sensor_data",
                "tags": {
                    "station_id": str(station_id),
                    "sensor_type": "ph",
                    "unit": "pH"
                },
                "fields": {
                    "_value": round(7.0 + random.uniform(-0.5, 0.5), 2)
                },
                "time": timestamp
            },
            {
                "measurement": "sensor_data",
                "tags": {
                    "station_id": str(station_id),
                    "sensor_type": "turbidity",
                    "unit": "NTU"
                },
                "fields": {
                    "_value": round(random.uniform(0.1, 1.0), 2)
                },
                "time": timestamp
            },
            {
                "measurement": "sensor_data",
                "tags": {
                    "station_id": str(station_id),
                    "sensor_type": "residual_chlorine",
                    "unit": "mg/L"
                },
                "fields": {
                    "_value": round(random.uniform(0.3, 0.8), 2)
                },
                "time": timestamp
            }
        ])
        
        return points
    
    def generate_historical_data(self, days: int = 7):
        """生成历史数据，默认7天"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        print(f"开始生成 {days} 天的历史数据...")
        
        current_time = start_time
        total_points = 0
        
        while current_time <= end_time:
            for station in self.stations:
                points = self.generate_sensor_data(station.id, current_time)
                influx_write_api.write(
                    bucket=settings.INFLUXDB_BUCKET,
                    org=settings.INFLUXDB_ORG,
                    record=points
                )
                total_points += len(points)
            
            # 10分钟间隔
            current_time += timedelta(minutes=10)
            
            if (current_time - start_time).total_seconds() % 3600 == 0:
                print(f"已生成到 {current_time.strftime('%Y-%m-%d %H:%M')}, 共 {total_points} 条数据")
        
        print(f"历史数据生成完成，共 {total_points} 条数据点")
    
    async def run_real_time_simulation(self):
        """运行实时数据模拟，每10分钟生成一次数据"""
        print("启动实时数据模拟...")
        while True:
            timestamp = datetime.utcnow()
            total_points = 0
            
            for station in self.stations:
                points = self.generate_sensor_data(station.id, timestamp)
                influx_write_api.write(
                    bucket=settings.INFLUXDB_BUCKET,
                    org=settings.INFLUXDB_ORG,
                    record=points
                )
                total_points += len(points)
            
            print(f"[{timestamp.strftime('%Y-%m-%d %H:%M')}] 已生成 {len(self.stations)} 个泵站的 {total_points} 条数据")
            
            # 等待10分钟
            await asyncio.sleep(settings.DATA_COLLECTION_INTERVAL)

# 初始化模拟器
simulator = DataSimulator()

if __name__ == "__main__":
    # 生成7天历史数据
    simulator.generate_historical_data(days=7)
    
    # 运行实时模拟
    import asyncio
    asyncio.run(simulator.run_real_time_simulation())
