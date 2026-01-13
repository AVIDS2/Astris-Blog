@echo off
REM ================================
REM 快速部署脚本 (Windows)
REM 用法: deploy.bat
REM ================================

echo 🚀 D.Will Blog 部署脚本 (Windows)
echo ========================

REM 检查 .env 文件
if not exist .env (
    echo ❌ 错误: 未找到 .env 文件
    echo 请复制 .env.example 为 .env 并填入配置:
    echo   copy .env.example .env
    echo   notepad .env
    exit /b 1
)

REM 创建必要的目录
echo 📁 创建数据目录...
if not exist data mkdir data
if not exist uploads mkdir uploads

REM 构建并启动
echo 🐳 构建 Docker 镜像...
docker-compose build
if %errorlevel% neq 0 (
    echo ❌ 构建失败！
    exit /b 1
)

echo 🚀 启动服务...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ 启动失败！
    exit /b 1
)

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 5 /nobreak > nul

REM 健康检查
echo 🔍 健康检查...
curl -s http://localhost:8000/api/health | findstr "ok" > nul
if %errorlevel% equ 0 (
    echo ✅ 部署成功！
    echo.
    echo 📌 访问地址:
    echo    - 前端: http://localhost:8000/
    echo    - 管理后台: http://localhost:8000/admin/
    echo    - API: http://localhost:8000/api/health
    echo.
    echo 📝 查看日志: docker-compose logs -f
) else (
    echo ❌ 健康检查失败，请检查日志:
    echo    docker-compose logs -f
    exit /b 1
)
