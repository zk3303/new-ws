from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    DB_URL: str = "mysql+pymysql://root:Water123456@localhost:3306/water_system?charset=utf8mb4"
    
    # InfluxDB配置
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = "XE6JVnKHp_oZUZ09AHKwHiPTZyEXmD3goUBGjdmWzEOI8DLvsoqmZLCiQDuAsbrlKlmQBYPlhgMOeVW0h0c8Zw=="
    INFLUXDB_ORG: str = "water"
    INFLUXDB_BUCKET: str = "sensor_data"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-keep-it-safe"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # MQTT配置
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = "admin"
    MQTT_PASSWORD: str = "Water123456"
    
    # 碳足迹配置
    CARBON_EMISSION_FACTOR: float = 0.5839  # 电网排放因子 tCO₂/MWh
    
    # 系统配置
    DATA_COLLECTION_INTERVAL: int = 600  # 10分钟，单位秒
    PUMP_COUNT: int = 20  # 支持的泵站数量

settings = Settings()
