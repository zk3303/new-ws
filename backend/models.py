from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# 用户模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(20), default="operator")  # admin/operator/visitor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 泵站模型
class PumpStation(Base):
    __tablename__ = "pump_stations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    address = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String(20), default="online")  # online/offline/maintenance
    capacity = Column(Float)  # 设计供水能力 m³/h
    installed_power = Column(Float)  # 装机容量 kW
    contact_person = Column(String(50))
    contact_phone = Column(String(20))
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    devices = relationship("Device", back_populates="station")
    alarms = relationship("Alarm", back_populates="station")

# 设备模型
class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("pump_stations.id"))
    name = Column(String(100), index=True)
    device_type = Column(String(50))  # pump/valve/sensor/meter
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)
    status = Column(String(20), default="running")  # running/standby/fault/maintenance
    installation_date = Column(DateTime)
    last_maintenance = Column(DateTime, nullable=True)
    next_maintenance = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    station = relationship("PumpStation", back_populates="devices")
    sensors = relationship("Sensor", back_populates="device")

# 传感器模型
class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    name = Column(String(100), index=True)
    sensor_type = Column(String(50))  # pressure/flow/temp/quality/electricity
    unit = Column(String(20))
    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)
    status = Column(String(20), default="normal")  # normal/abnormal/fault
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    device = relationship("Device", back_populates="sensors")

# 告警模型
class Alarm(Base):
    __tablename__ = "alarms"
    
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("pump_stations.id"))
    device_id = Column(Integer, nullable=True)
    sensor_id = Column(Integer, nullable=True)
    alarm_type = Column(String(50))  # over_threshold/communication_fault/device_fault
    level = Column(String(20))  # critical/warning/info
    title = Column(String(255))
    description = Column(Text)
    status = Column(String(20), default="pending")  # pending/processing/resolved/closed
    triggered_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    station = relationship("PumpStation", back_populates="alarms")
    work_order = relationship("WorkOrder", back_populates="alarm", uselist=False)

# 工单模型
class WorkOrder(Base):
    __tablename__ = "work_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    alarm_id = Column(Integer, ForeignKey("alarms.id"), nullable=True)
    title = Column(String(255))
    description = Column(Text)
    status = Column(String(20), default="pending")  # pending/assigned/in_progress/completed/verified
    priority = Column(String(20), default="medium")  # high/medium/low
    assign_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    completed_at = Column(DateTime, nullable=True)
    completion_note = Column(Text, nullable=True)
    expected_completion = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    alarm = relationship("Alarm", back_populates="work_order")

# 碳足迹配置
class CarbonConfig(Base):
    __tablename__ = "carbon_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    emission_factor = Column(Float, default=0.5839)  # tCO₂/MWh
    water_carbon_factor = Column(Float, default=0.00025)  # tCO₂/m³ 供水碳排放因子
    chemical_carbon_factor = Column(Float, default=0.001)  # tCO₂/kg 化学品碳排放因子
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
