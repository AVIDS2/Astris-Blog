"""更新数据库中的缩略图路径"""
import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.database import async_session
from app.models import Photo
from sqlalchemy import select

async def update_thumbnails():
    async with async_session() as db:
        result = await db.execute(select(Photo))
        photos = result.scalars().all()
        updated = 0
        for photo in photos:
            if photo.url and not photo.thumbnail:
                name = os.path.splitext(os.path.basename(photo.url))[0]
                thumb_path = f"/uploads/photos/thumbnails/{name}_thumb.jpg"
                photo.thumbnail = thumb_path
                updated += 1
                print(f"  更新: {photo.url} -> {thumb_path}")
        await db.commit()
        print(f"\n✅ 更新了 {updated} 张照片的缩略图路径")

if __name__ == "__main__":
    asyncio.run(update_thumbnails())
