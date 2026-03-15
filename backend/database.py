from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from influxdb_client import InfluxDBClient
from config import settings

# MySQL数据库配置
SQLALCHEMY_DATABASE_URL = settings.DB_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# InfluxDB配置
influx_client = InfluxDBClient(
    url=settings.INFLUXDB_URL,
    token=settings.INFLUXDB_TOKEN,
    org=settings.INFLUXDB_ORG
)
influx_write_api = influx_client.write_api()
influx_query_api = influx_client.query_api()

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
