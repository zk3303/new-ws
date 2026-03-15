from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
import numpy as np
from config import settings
from database import influx_query_api, influx_write_api
from models import CarbonConfig

class CarbonCalculator:
    """碳足迹计算器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config = self._get_config()
    
    def _get_config(self):
        """获取碳足迹配置"""
        config = self.db.query(CarbonConfig).first()
        if not config:
            config = CarbonConfig()
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        return config
    
    def calculate_emissions(self, energy_kwh: float, water_m3: float = 0, chemical_kg: float = 0) -> dict:
        """
        计算总碳排放量
        :param energy_kwh: 耗电量 kWh
        :param water_m3: 用水量 m³
        :param chemical_kg: 化学品消耗量 kg
        :return: 碳排放详情
        """
        # 转换单位：kWh -> MWh
        energy_mwh = energy_kwh / 1000
        
        # 计算各部分碳排放
        energy_emissions = energy_mwh * self.config.emission_factor
        water_emissions = water_m3 * self.config.water_carbon_factor
        chemical_emissions = chemical_kg * self.config.chemical_carbon_factor
        
        total_emissions = energy_emissions + water_emissions + chemical_emissions
        
        return {
            "total_emissions": round(total_emissions, 6),  # tCO₂
            "energy_emissions": round(energy_emissions, 6),
            "water_emissions": round(water_emissions, 6),
            "chemical_emissions": round(chemical_emissions, 6),
            "energy_kwh": energy_kwh,
            "water_m3": water_m3,
            "chemical_kg": chemical_kg,
            "emission_factor": self.config.emission_factor
        }
    
    def get_station_emissions(self, station_id: int, start_time: datetime = None, end_time: datetime = None) -> dict:
        """获取指定泵站的碳足迹数据"""
        if not end_time:
            end_time = datetime.utcnow()
        if not start_time:
            start_time = end_time - timedelta(days=30)
        
        # 查询时序数据库中的能耗和流量数据
        query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
          |> range(start: {int(start_time.timestamp())}, stop: {int(end_time.timestamp())})
          |> filter(fn: (r) => r["station_id"] == "{station_id}")
          |> filter(fn: (r) => r["_measurement"] == "sensor_data")
          |> filter(fn: (r) => r["_field"] == "active_power" or r["_field"] == "flow_rate")
          |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''
        
        tables = influx_query_api.query(query, org=settings.INFLUXDB_ORG)
        
        total_energy = 0  # kWh
        total_water = 0   # m³
        data_points = []
        
        for table in tables:
            for record in table.records:
                field = record.get_field()
                value = record.get_value()
                time = record.get_time()
                
                if field == "active_power":
                    # 功率 kW × 1小时 = kWh
                    total_energy += value * 1
                elif field == "flow_rate":
                    # 流量 m³/h × 1小时 = m³
                    total_water += value * 1
                
                data_points.append({
                    "time": time.isoformat(),
                    "field": field,
                    "value": value
                })
        
        # 计算碳排放
        emissions = self.calculate_emissions(total_energy, total_water)
        
        # 计算碳排放强度（单位供水碳排放）
        emission_intensity = emissions["total_emissions"] / total_water if total_water > 0 else 0
        
        return {
            "station_id": station_id,
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "days": (end_time - start_time).days
            },
            "total_emissions": emissions["total_emissions"],
            "energy_emissions": emissions["energy_emissions"],
            "water_emissions": emissions["water_emissions"],
            "total_energy_kwh": round(total_energy, 2),
            "total_water_m3": round(total_water, 2),
            "emission_intensity": round(emission_intensity, 6),  # tCO₂/m³
            "emission_factor": self.config.emission_factor,
            "data_points": data_points
        }
    
    def get_all_stations_emissions(self, start_time: datetime = None, end_time: datetime = None) -> list:
        """获取所有泵站的碳排放排名"""
        if not end_time:
            end_time = datetime.utcnow()
        if not start_time:
            start_time = end_time - timedelta(days=30)
        
        # 查询所有泵站的能耗数据
        query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
          |> range(start: {int(start_time.timestamp())}, stop: {int(end_time.timestamp())})
          |> filter(fn: (r) => r["_measurement"] == "sensor_data")
          |> filter(fn: (r) => r["_field"] == "active_power" or r["_field"] == "flow_rate")
          |> group(columns: ["station_id"])
          |> sum()
        '''
        
        tables = influx_query_api.query(query, org=settings.INFLUXDB_ORG)
        
        station_data = {}
        
        for table in tables:
            for record in table.records:
                station_id = record.values["station_id"]
                field = record.get_field()
                value = record.get_value()
                
                if station_id not in station_data:
                    station_data[station_id] = {"energy": 0, "water": 0}
                
                if field == "active_power":
                    station_data[station_id]["energy"] = value * 1  # kWh
                elif field == "flow_rate":
                    station_data[station_id]["water"] = value * 1   # m³
        
        # 计算每个泵站的碳排放
        result = []
        for station_id, data in station_data.items():
            emissions = self.calculate_emissions(data["energy"], data["water"])
            intensity = emissions["total_emissions"] / data["water"] if data["water"] > 0 else 0
            
            result.append({
                "station_id": int(station_id),
                "total_emissions": emissions["total_emissions"],
                "energy_kwh": round(data["energy"], 2),
                "water_m3": round(data["water"], 2),
                "emission_intensity": round(intensity, 6),
                "rank": 0  # 后续排序
            })
        
        # 按总碳排放排序
        result.sort(key=lambda x: x["total_emissions"], reverse=True)
        for i, item in enumerate(result):
            item["rank"] = i + 1
        
        return result
    
    def get_trend_data(self, station_id: int = None, days: int = 30) -> dict:
        """获取碳足迹趋势数据（按天）"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        station_filter = f'|> filter(fn: (r) => r["station_id"] == "{station_id}")' if station_id else ''
        
        query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
          |> range(start: {int(start_time.timestamp())}, stop: {int(end_time.timestamp())})
          |> filter(fn: (r) => r["_measurement"] == "sensor_data")
          |> filter(fn: (r) => r["_field"] == "active_power" or r["_field"] == "flow_rate")
          {station_filter}
          |> aggregateWindow(every: 1d, fn: sum)
          |> yield(name: "daily_sum")
        '''
        
        tables = influx_query_api.query(query, org=settings.INFLUXDB_ORG)
        
        daily_data = {}
        
        for table in tables:
            for record in table.records:
                date = record.get_time().strftime("%Y-%m-%d")
                field = record.get_field()
                value = record.get_value()
                
                if date not in daily_data:
                    daily_data[date] = {"energy": 0, "water": 0}
                
                if field == "active_power":
                    daily_data[date]["energy"] = value  # kWh/天
                elif field == "flow_rate":
                    daily_data[date]["water"] = value   # m³/天
        
        # 计算每天的碳排放
        trend = []
        for date, data in sorted(daily_data.items()):
            emissions = self.calculate_emissions(data["energy"], data["water"])
            trend.append({
                "date": date,
                "total_emissions": emissions["total_emissions"],
                "energy_emissions": emissions["energy_emissions"],
                "water_emissions": emissions["water_emissions"],
                "energy_kwh": round(data["energy"], 2),
                "water_m3": round(data["water"], 2)
            })
        
        return {
            "days": days,
            "trend": trend,
            "total_emissions": sum(item["total_emissions"] for item in trend),
            "avg_daily_emissions": round(sum(item["total_emissions"] for item in trend) / len(trend), 6) if trend else 0
        }
    
    def calculate_reduction_potential(self, station_id: int) -> dict:
        """计算节能降碳潜力"""
        # 获取过去30天数据
        data = self.get_station_emissions(station_id)
        
        # 假设优化潜力：节能15%，能效提升
        current_intensity = data["emission_intensity"]
        potential_reduction_rate = 0.15  # 15% 降碳潜力
        potential_reduction = data["total_emissions"] * potential_reduction_rate
        
        return {
            "station_id": station_id,
            "current_total_emissions": data["total_emissions"],
            "current_emission_intensity": current_intensity,
            "potential_reduction_rate": potential_reduction_rate,
            "annual_reduction_potential": round(potential_reduction * 12, 4),  # 年降碳潜力（吨）
            "annual_cost_saving": round(potential_reduction * 50 * 12, 2),  # 假设碳价50元/吨，年节约成本
            "recommendation": "建议进行泵组变频改造、管网漏损治理、优化调度策略，可实现15%以上的碳减排。"
        }
