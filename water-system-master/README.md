# 智慧水务系统

基于物联网技术的智慧水务管理系统

## 技术栈

- 后端：Python + FastAPI
- 前端：Vue.js 3.0 + Three.js + ECharts
- 数据库：SQLite（演示）/ MySQL（生产）
- 通信：MQTT（可选）
- 容器：Docker + Docker Compose

## 快速部署

### 前置要求

- Docker
- Docker Compose

### 部署步骤

1. 克隆项目
```bash
git clone https://github.com/zk3303/water-system.git
cd water-system
```

2. 一键启动（演示模式）
```bash
docker-compose up -d
```

3. 访问系统
- 前端：http://localhost
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 生产环境部署

1. 修改 `docker-compose.yml`，启用 MySQL 和 MQTT

2. 重新构建并启动
```bash
docker-compose up -d --build
```

## Docker 命令

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

## API 接口文档

启动后访问：http://localhost:8000/docs

## 论文相关

本系统是学位论文《智慧水务管理系统设计与实现》的实现项目。
