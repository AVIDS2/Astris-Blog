from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "My Blog API"
    debug: bool = True
    
    # 数据库配置 (生产环境使用 data 目录便于 Docker volume 持久化)
    database_url: str = "sqlite+aiosqlite:///./blog.db"
    
    # JWT 配置
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 天
    
    # 管理员默认账户（请在 .env 文件或环境变量中配置）
    admin_username: str = "admin"
    admin_password: str = "change-me-immediately"  # ⚠️ 部署时必须修改！
    
    # CORS 配置 (逗号分隔的域名列表)
    cors_origins: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """将逗号分隔的 CORS 域名转换为列表"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()

