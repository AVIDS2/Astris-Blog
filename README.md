# D.Will Blog

一个基于 Astro + FastAPI + Vue 的全栈个人博客系统。

## 🌟 功能特性

- **前端**：Astro SSR + Svelte 组件 + TailwindCSS
- **后端**：FastAPI + SQLite (异步)
- **管理后台**：Vue 3 + Element Plus
- **其他**：Live2D 看板娘、樱花特效、音乐播放器、全屏壁纸模式

## 🚀 快速开始

### 开发环境

```bash
# 1. 启动后端
cd server
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2. 启动前端
cd client
pnpm install
pnpm dev

# 3. 启动管理后台开发服务器
cd server/admin
npm install
npm run dev
```

### 生产部署

请参阅 [DEPLOY.md](./DEPLOY.md) 获取详细的部署指南。

```bash
# 快速部署（需要 Docker）
cp .env.example .env  # 编辑 .env 文件填入真实配置
docker-compose up -d --build
```

## 📁 项目结构

```
my_blog/
├── client/              # Astro 前端
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── pages/       # 页面
│   │   ├── layouts/     # 布局
│   │   └── config.ts    # 站点配置
│   └── public/          # 静态资源
├── server/
│   ├── app/             # FastAPI 后端
│   │   ├── routers/     # API 路由
│   │   ├── models.py    # 数据模型
│   │   └── main.py      # 入口文件
│   └── admin/           # Vue 管理后台
├── Dockerfile           # Docker 构建文件
├── docker-compose.yml   # Docker Compose 配置
├── .env.example         # 环境变量模板
└── DEPLOY.md            # 部署文档
```

## ⚙️ 配置说明

主要配置文件：`client/src/config.ts`

- `siteURL`：你的站点 URL
- `banner`：首页 Banner 配置
- `pioConfig`：Live2D 看板娘配置
- `musicPlayerConfig`：音乐播放器配置

## 📝 License

MIT
