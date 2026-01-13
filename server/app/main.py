import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.database import init_db, async_session
from app.models import User
from app.auth import get_password_hash
from app.config import get_settings
from app.routers import posts, admin, bilibili, tools, albums, search, about, banner, friends

settings = get_settings()


async def create_default_admin():
    """创建默认管理员账户"""
    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == settings.admin_username))
        user = result.scalar_one_or_none()
        
        if not user:
            admin_user = User(
                username=settings.admin_username,
                password_hash=get_password_hash(settings.admin_password),
                email="admin@example.com"
            )
            db.add(admin_user)
            await db.commit()
            print(f"✅ 创建默认管理员: {settings.admin_username}")
        else:
            print(f"ℹ️ 管理员已存在: {settings.admin_username}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("🚀 正在初始化数据库...")
    await init_db()
    await create_default_admin()
    print("✅ 数据库初始化完成")
    
    yield
    
    # 关闭时
    print("👋 应用关闭")


app = FastAPI(
    title=settings.app_name,
    description="个人博客 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # 从环境变量读取
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(posts.router, prefix="/api", tags=["公开接口"])
app.include_router(search.router, prefix="/api", tags=["搜索接口"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理接口"])
app.include_router(bilibili.router, tags=["Bilibili 代理"])
app.include_router(tools.router, tags=["工具收藏"])
app.include_router(albums.router, tags=["相册"])
app.include_router(about.router, prefix="/api/admin", tags=["关于页面"])
app.include_router(banner.router, prefix="/api/admin", tags=["Banner管理"])
app.include_router(banner.router, prefix="/api", tags=["Banner公开接口"])  # 公开接口
app.include_router(friends.router, prefix="/api", tags=["友链"])


# 获取项目根目录 (Docker 环境下为 /app)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 静态文件服务（管理后台）
admin_dist = os.path.join(BASE_DIR, "static", "admin")
if os.path.exists(admin_dist):
    app.mount("/admin", StaticFiles(directory=admin_dist, html=True), name="admin")
else:
    print(f"⚠️ 警告: 未找到管理后台目录: {admin_dist}")

# 静态文件服务（上传的文件）
uploads_dir = os.path.join(BASE_DIR, "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 静态文件服务（前端静态资源）
client_public_assets = os.path.join(BASE_DIR, "client", "public", "assets")
if os.path.exists(client_public_assets):
    app.mount("/assets", StaticFiles(directory=client_public_assets), name="assets")

client_public_images = os.path.join(BASE_DIR, "client", "public", "images")
if os.path.exists(client_public_images):
    app.mount("/images", StaticFiles(directory=client_public_images), name="images")

# 静态文件服务（博客前端）- 这是最后的兜底处理，负责主页渲染
client_dist = os.path.join(BASE_DIR, "client", "dist", "client")
if os.path.exists(client_dist):
    app.mount("/", StaticFiles(directory=client_dist, html=True), name="client")
else:
    print(f"⚠️ 警告: 未找到前端构建目录: {client_dist}")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "app": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
