"""
相册 API
支持相册管理和图片上传
"""
import os
import uuid
import shutil
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Album, Photo
from app.auth import get_current_user

router = APIRouter(prefix="/api/albums", tags=["相册"])

# 上传目录 - 注意路径要与 main.py 中的静态文件服务一致
# routers 在 app/routers/ 下，所以需要往上走两级到 server/uploads
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "photos")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ========== Pydantic 模型 ==========

class PhotoResponse(BaseModel):
    id: int
    url: str
    thumbnail: Optional[str]
    title: Optional[str]
    description: Optional[str]
    sort_order: int

    class Config:
        from_attributes = True


class AlbumResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    cover: Optional[str]
    sort_order: int
    is_visible: bool
    photo_count: int = 0

    class Config:
        from_attributes = True


class AlbumDetailResponse(AlbumResponse):
    photos: List[PhotoResponse] = []


class AlbumCreate(BaseModel):
    name: str
    description: Optional[str] = None
    cover: Optional[str] = None
    sort_order: int = 0
    is_visible: bool = True


class AlbumUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cover: Optional[str] = None
    sort_order: Optional[int] = None
    is_visible: Optional[bool] = None


# ========== 公开接口 ==========

@router.get("")
async def get_albums(db: AsyncSession = Depends(get_db)):
    """获取所有可见相册"""
    result = await db.execute(
        select(Album)
        .where(Album.is_visible == True)
        .options(selectinload(Album.photos))
        .order_by(Album.sort_order)
    )
    albums = result.scalars().all()
    
    return [
        AlbumResponse(
            id=a.id,
            name=a.name,
            description=a.description,
            cover=a.cover or (a.photos[0].url if a.photos else None),
            sort_order=a.sort_order,
            is_visible=a.is_visible,
            photo_count=len(a.photos)
        )
        for a in albums
    ]


@router.get("/{album_id}")
async def get_album_detail(album_id: int, db: AsyncSession = Depends(get_db)):
    """获取相册详情（含照片）"""
    result = await db.execute(
        select(Album)
        .where(Album.id == album_id)
        .options(selectinload(Album.photos))
    )
    album = result.scalar_one_or_none()
    
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    return AlbumDetailResponse(
        id=album.id,
        name=album.name,
        description=album.description,
        cover=album.cover,
        sort_order=album.sort_order,
        is_visible=album.is_visible,
        photo_count=len(album.photos),
        photos=[PhotoResponse.model_validate(p) for p in sorted(album.photos, key=lambda x: x.sort_order)]
    )


# ========== 管理接口 ==========

@router.get("/admin/all")
async def get_all_albums(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """获取所有相册（包括隐藏的）"""
    result = await db.execute(
        select(Album)
        .options(selectinload(Album.photos))
        .order_by(Album.sort_order)
    )
    albums = result.scalars().all()
    
    return [
        AlbumResponse(
            id=a.id,
            name=a.name,
            description=a.description,
            cover=a.cover or (a.photos[0].url if a.photos else None),
            sort_order=a.sort_order,
            is_visible=a.is_visible,
            photo_count=len(a.photos)
        )
        for a in albums
    ]


@router.post("/admin")
async def create_album(
    album: AlbumCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """创建新相册"""
    new_album = Album(**album.model_dump())
    db.add(new_album)
    await db.commit()
    await db.refresh(new_album)
    return AlbumResponse(
        id=new_album.id,
        name=new_album.name,
        description=new_album.description,
        cover=new_album.cover,
        sort_order=new_album.sort_order,
        is_visible=new_album.is_visible,
        photo_count=0
    )


@router.put("/admin/{album_id}")
async def update_album(
    album_id: int,
    album: AlbumUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """更新相册"""
    result = await db.execute(select(Album).where(Album.id == album_id))
    db_album = result.scalar_one_or_none()
    
    if not db_album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    for key, value in album.model_dump(exclude_unset=True).items():
        setattr(db_album, key, value)
    
    await db.commit()
    await db.refresh(db_album)
    return {"message": "Album updated"}


@router.delete("/admin/{album_id}")
async def delete_album(
    album_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """删除相册（会同时删除所有照片）"""
    result = await db.execute(select(Album).where(Album.id == album_id))
    db_album = result.scalar_one_or_none()
    
    if not db_album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    await db.delete(db_album)
    await db.commit()
    return {"message": "Album deleted"}


# ========== 照片上传 ==========

@router.post("/admin/{album_id}/photos")
async def upload_photos(
    album_id: int,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """上传照片到相册（自动生成缩略图）"""
    from PIL import Image
    import io
    
    # 缩略图配置
    THUMB_SIZE = (400, 400)  # 缩略图最大尺寸
    THUMB_QUALITY = 85  # JPEG 压缩质量
    
    # 检查相册是否存在
    result = await db.execute(select(Album).where(Album.id == album_id))
    album = result.scalar_one_or_none()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    # 确保缩略图目录存在
    thumb_dir = os.path.join(UPLOAD_DIR, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)
    
    uploaded = []
    for file in files:
        # 生成唯一文件名
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            continue
        
        unique_id = uuid.uuid4().hex
        filename = f"{unique_id}{ext}"
        thumb_filename = f"{unique_id}_thumb.jpg"  # 缩略图统一用 jpg
        
        filepath = os.path.join(UPLOAD_DIR, filename)
        thumb_filepath = os.path.join(thumb_dir, thumb_filename)
        
        # 读取文件内容
        content = await file.read()
        
        # 保存原图
        with open(filepath, "wb") as f:
            f.write(content)
        
        # 生成缩略图
        try:
            img = Image.open(io.BytesIO(content))
            
            # 处理 EXIF 旋转
            try:
                from PIL import ExifTags
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
            
            # 转换为 RGB（处理 RGBA/P 模式）
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # 生成缩略图（保持比例）
            img.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
            img.save(thumb_filepath, "JPEG", quality=THUMB_QUALITY, optimize=True)
            
            thumb_url = f"/uploads/photos/thumbnails/{thumb_filename}"
        except Exception as e:
            print(f"Failed to generate thumbnail for {filename}: {e}")
            thumb_url = None
        
        # 创建数据库记录
        photo = Photo(
            url=f"/uploads/photos/{filename}",
            thumbnail=thumb_url,
            album_id=album_id,
            title=os.path.splitext(file.filename)[0]
        )
        db.add(photo)
        uploaded.append(filename)
    
    await db.commit()
    return {"message": f"Uploaded {len(uploaded)} photos", "files": uploaded}


@router.delete("/admin/photos/{photo_id}")
async def delete_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """删除照片"""
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # 尝试删除文件
    try:
        filepath = os.path.join(UPLOAD_DIR, os.path.basename(photo.url))
        if os.path.exists(filepath):
            os.remove(filepath)
    except:
        pass
    
    await db.delete(photo)
    await db.commit()
    return {"message": "Photo deleted"}
