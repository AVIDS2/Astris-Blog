# ================================
# 博客全栈 Dockerfile
# 包含：FastAPI 后端 + Astro 前端 + Vue 管理后台
# ================================

# === 阶段1：构建前端 ===
FROM node:20-alpine AS frontend-builder

WORKDIR /app/client

# 复制前端依赖文件
COPY client/package.json client/pnpm-lock.yaml ./

# 安装 pnpm 和依赖
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# 复制前端源码并构建
COPY client/ ./

# 设置构建时的 API 地址（SSR 构建时使用）
ENV API_URL=http://localhost:8000

RUN pnpm build


# === 阶段2：构建管理后台 ===
FROM node:20-alpine AS admin-builder

WORKDIR /app/admin

# 复制管理后台依赖文件
COPY server/admin/package.json server/admin/package-lock.json ./

# 安装依赖
RUN npm ci

# 复制管理后台源码并构建
COPY server/admin/ ./
RUN npm run build


# === 阶段3：最终运行镜像 ===
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（如有需要可添加）
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 复制 Python 依赖文件
COPY server/requirements.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端源码
COPY server/app ./app

# 从构建阶段复制前端构建产物
COPY --from=frontend-builder /app/client/dist ./client/dist

# 从构建阶段复制管理后台构建产物
COPY --from=admin-builder /app/admin/dist ./static/admin

# 复制前端静态资源（Banner 图片等）
COPY client/public/assets ./client/public/assets
COPY client/public/images ./client/public/images

# 创建数据目录（用于 SQLite 和上传文件）
RUN mkdir -p /app/data /app/uploads/photos/thumbnails

# 设置环境变量默认值
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite+aiosqlite:///./data/blog.db
ENV DEBUG=false

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
