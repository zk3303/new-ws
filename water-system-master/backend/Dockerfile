# 后端 Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY backend/ .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main.py"]
