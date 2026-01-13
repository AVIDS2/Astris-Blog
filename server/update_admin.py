"""更新管理员账号"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import async_session
from app.models import User
from app.auth import get_password_hash
from sqlalchemy import select

async def update_admin():
    async with async_session() as db:
        # 查找现有的 admin 用户
        result = await db.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one_or_none()
        
        if user:
            # 更新用户名和密码
            user.username = "avids2"
            user.password_hash = get_password_hash("788788")
            await db.commit()
            print("✅ 管理员账号已更新:")
            print(f"   用户名: avids2")
            print(f"   密码: 788788")
        else:
            # 如果没有 admin，创建新用户
            new_user = User(
                username="avids2",
                password_hash=get_password_hash("788788"),
                email="admin@example.com"
            )
            db.add(new_user)
            await db.commit()
            print("✅ 创建新管理员账号:")
            print(f"   用户名: avids2")
            print(f"   密码: 788788")

if __name__ == "__main__":
    asyncio.run(update_admin())
