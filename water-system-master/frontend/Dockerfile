# 前端 Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# 安装依赖
COPY frontend/package.json frontend/pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install

# 复制代码
COPY frontend/ .

# 构建
RUN pnpm run build

# Nginx 生产镜像
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
