#!/bin/bash
# ================================
# 快速部署脚本
# 用法: ./deploy.sh
# ================================

set -e

echo "🚀 D.Will Blog 部署脚本"
echo "========================"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "❌ 错误: 未找到 .env 文件"
    echo "请复制 .env.example 为 .env 并填入配置："
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# 检查必要的环境变量
source .env
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-random-secret-key-here-64-chars-minimum" ]; then
    echo "❌ 错误: 请在 .env 中设置 SECRET_KEY"
    echo "生成命令: openssl rand -hex 32"
    exit 1
fi

if [ -z "$ADMIN_PASSWORD" ] || [ "$ADMIN_PASSWORD" = "your-secure-password-here" ]; then
    echo "❌ 错误: 请在 .env 中设置 ADMIN_PASSWORD"
    exit 1
fi

# 创建必要的目录
echo "📁 创建数据目录..."
mkdir -p data uploads

# 构建并启动
echo "🐳 构建 Docker 镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 健康检查
echo "🔍 健康检查..."
if curl -s http://localhost:8000/api/health | grep -q '"status":"ok"'; then
    echo "✅ 部署成功！"
    echo ""
    echo "📌 访问地址:"
    echo "   - 前端: http://localhost:8000/"
    echo "   - 管理后台: http://localhost:8000/admin/"
    echo "   - API: http://localhost:8000/api/health"
    echo ""
    echo "📝 查看日志: docker-compose logs -f"
else
    echo "❌ 健康检查失败，请检查日志:"
    echo "   docker-compose logs -f"
    exit 1
fi
