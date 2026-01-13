"""
修复数据库中的图片硬编码路径
将 http://localhost:8000/uploads 转换为相对路径 /uploads
"""
import asyncio
import sys
import re
sys.path.insert(0, '.')

from app.database import async_session
from app.models import Post

async def fix_image_paths():
    async with async_session() as db:
        from sqlalchemy import select
        result = await db.execute(select(Post))
        posts = result.scalars().all()
        
        count = 0
        for post in posts:
            # 替换正文中的硬编码
            new_content = re.sub(r'http://localhost:8000/uploads', '/uploads', post.content)
            
            # 修复封面图封面硬编码
            new_cover = post.cover_image
            if post.cover_image and 'localhost:8000' in post.cover_image:
                new_cover = re.sub(r'http://localhost:8000/uploads', '/uploads', post.cover_image)
            
            if new_content != post.content or new_cover != post.cover_image:
                post.content = new_content
                post.cover_image = new_cover
                count += 1
        
        if count > 0:
            await db.commit()
            print(f"✅ 成功修复 {count} 篇文章中的图片路径硬编码！")
        else:
            print("✨ 没有发现需要修复的硬编码路径。")

if __name__ == "__main__":
    asyncio.run(fix_image_paths())
