# ================================
# 博客全栈 Dockerfile
# 包含：Astro 前端(SSR) + FastAPI 后端 + Vue 管理后台
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

# 设置构建时的 API 地址
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
FROM node:20-alpine

WORKDIR /app

# 安装 Python 和必要的系统依赖
RUN apk add --no-cache python3 py3-pip

# 复制 Python 依赖文件并安装
COPY server/requirements.txt ./
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# 复制后端源码
COPY server/app ./app

# 从构建阶段复制前端构建产物（SSR 模式）
COPY --from=frontend-builder /app/client/dist ./client/dist
COPY --from=frontend-builder /app/client/node_modules ./client/node_modules
COPY --from=frontend-builder /app/client/package.json ./client/package.json

# 从构建阶段复制管理后台构建产物
COPY --from=admin-builder /app/static/admin ./static/admin

# 复制前端静态资源（Banner 图片等）
COPY client/public/assets ./client/public/assets
COPY client/public/images ./client/public/images

# 创建数据目录（用于 SQLite 和上传文件）
RUN mkdir -p /app/data /app/uploads/photos/thumbnails

# 设置环境变量
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite+aiosqlite:///./data/blog.db
ENV DEBUG=false
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=4321

# 暴露端口（4321: Astro前端, 8000: FastAPI后端）
EXPOSE 4321 8000

# 复制启动脚本
COPY start.sh ./
RUN chmod +x start.sh

# 启动命令
CMD ["./start.sh"]
