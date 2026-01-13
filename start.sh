#!/bin/sh
# 启动脚本：同时运行 Astro 前端和 FastAPI 后端

echo "🚀 启动 Astris Blog..."

# 后台启动 FastAPI 后端
echo "📦 启动 FastAPI 后端 (端口 8000)..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 等待后端启动
sleep 2

# 前台启动 Astro 前端
echo "🌐 启动 Astro 前端 (端口 4321)..."
cd /app/client/dist/server
node entry.mjs
