"""
为现有照片生成缩略图的一次性脚本
运行方法: python generate_thumbnails.py
"""
import os
import sys
from PIL import Image, ExifTags

# 配置
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads", "photos")
THUMB_DIR = os.path.join(UPLOAD_DIR, "thumbnails")
THUMB_SIZE = (400, 400)
THUMB_QUALITY = 85

# 确保目录存在
os.makedirs(THUMB_DIR, exist_ok=True)

def generate_thumbnail(filepath):
    """为单张图片生成缩略图"""
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    thumb_filename = f"{name}_thumb.jpg"
    thumb_path = os.path.join(THUMB_DIR, thumb_filename)
    
    # 跳过已存在的缩略图
    if os.path.exists(thumb_path):
        print(f"  跳过 (已存在): {thumb_filename}")
        return thumb_filename
    
    try:
        img = Image.open(filepath)
        
        # 处理 EXIF 旋转
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(img._getexif().items()) if hasattr(img, '_getexif') and img._getexif() else {}
            if orientation in exif:
                if exif[orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    img = img.rotate(90, expand=True)
        except:
            pass
        
        # 转换为 RGB
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # 生成缩略图
        img.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
        img.save(thumb_path, "JPEG", quality=THUMB_QUALITY, optimize=True)
        
        # 计算压缩比
        original_size = os.path.getsize(filepath)
        thumb_size = os.path.getsize(thumb_path)
        ratio = (1 - thumb_size / original_size) * 100
        
        print(f"  ✅ {filename}: {original_size/1024:.1f}KB → {thumb_size/1024:.1f}KB ({ratio:.1f}% 压缩)")
        return thumb_filename
        
    except Exception as e:
        print(f"  ❌ 失败: {filename} - {e}")
        return None

def main():
    print("=" * 50)
    print("📷 为现有照片生成缩略图")
    print("=" * 50)
    
    # 获取所有图片文件
    extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    photos = [
        f for f in os.listdir(UPLOAD_DIR) 
        if os.path.isfile(os.path.join(UPLOAD_DIR, f)) 
        and os.path.splitext(f)[1].lower() in extensions
    ]
    
    print(f"\n找到 {len(photos)} 张照片\n")
    
    success = 0
    for photo in photos:
        filepath = os.path.join(UPLOAD_DIR, photo)
        if generate_thumbnail(filepath):
            success += 1
    
    print(f"\n✅ 完成！成功生成 {success}/{len(photos)} 个缩略图")
    print(f"📁 缩略图目录: {THUMB_DIR}")
    
    # 提示更新数据库
    print("\n" + "=" * 50)
    print("⚠️  请运行以下命令更新数据库中的缩略图路径:")
    print("=" * 50)
    print("""
    在 Python 中执行:
    
    import asyncio
    from app.database import async_session
    from app.models import Photo
    from sqlalchemy import select, update
    import os
    
    async def update_thumbnails():
        async with async_session() as db:
            result = await db.execute(select(Photo))
            photos = result.scalars().all()
            for photo in photos:
                if photo.url:
                    name = os.path.splitext(os.path.basename(photo.url))[0]
                    photo.thumbnail = f"/uploads/photos/thumbnails/{name}_thumb.jpg"
            await db.commit()
            print(f"Updated {len(photos)} photos")
    
    asyncio.run(update_thumbnails())
    """)

if __name__ == "__main__":
    main()
