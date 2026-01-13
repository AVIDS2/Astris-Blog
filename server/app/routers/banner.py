# Banner 管理接口
import os
import json
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from PIL import Image
import io
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/banner", tags=["banner"])

# Banner 图片存储路径
CLIENT_PUBLIC = Path(__file__).parent.parent.parent.parent / "client" / "public"
DESKTOP_BANNER_DIR = CLIENT_PUBLIC / "assets" / "desktop-banner"
MOBILE_BANNER_DIR = CLIENT_PUBLIC / "assets" / "mobile-banner"

# 缩略图目录
THUMBNAIL_DIR = Path(__file__).parent.parent.parent / "uploads" / "banner-thumbnails"
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

# 确保目录存在
DESKTOP_BANNER_DIR.mkdir(parents=True, exist_ok=True)
MOBILE_BANNER_DIR.mkdir(parents=True, exist_ok=True)


class BannerListResponse(BaseModel):
    desktop: List[str]
    mobile: List[str]


def get_banner_images(directory: Path) -> List[str]:
    """获取目录下的所有图片文件"""
    if not directory.exists():
        return []
    extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif'}
    images = []
    for f in directory.iterdir():
        if f.is_file() and f.suffix.lower() in extensions:
            images.append(f.name)
    return sorted(images)


def generate_thumbnail(image_path: Path, device: str) -> Path:
    """生成缩略图"""
    thumb_filename = f"{device}_{image_path.name}"
    thumb_path = THUMBNAIL_DIR / thumb_filename
    
    # 如果缩略图已存在且比原图新，直接返回
    if thumb_path.exists():
        if thumb_path.stat().st_mtime >= image_path.stat().st_mtime:
            return thumb_path
    
    try:
        with Image.open(image_path) as img:
            # 转换为 RGB（处理 RGBA 等格式）
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # 缩略图尺寸：宽度 400px，保持比例
            width = 400
            ratio = width / img.width
            height = int(img.height * ratio)
            
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            img.save(thumb_path, "JPEG", quality=70, optimize=True)
            
        return thumb_path
    except Exception as e:
        print(f"生成缩略图失败: {e}")
        return image_path  # 失败时返回原图


@router.get("", response_model=BannerListResponse)
async def get_banners(current_user: User = Depends(get_current_user)):
    """获取所有 banner 图片列表（需要登录）"""
    return BannerListResponse(
        desktop=get_banner_images(DESKTOP_BANNER_DIR),
        mobile=get_banner_images(MOBILE_BANNER_DIR)
    )


@router.get("/public", response_model=BannerListResponse)
async def get_public_banners():
    """获取所有 banner 图片列表（公开接口，供前端使用）"""
    return BannerListResponse(
        desktop=get_banner_images(DESKTOP_BANNER_DIR),
        mobile=get_banner_images(MOBILE_BANNER_DIR)
    )


@router.get("/thumbnail/{device}/{filename}")
async def get_banner_thumbnail(device: str, filename: str):
    """获取 Banner 缩略图（用于后台预览）"""
    if device not in ["desktop", "mobile"]:
        raise HTTPException(status_code=400, detail="设备类型必须是 desktop 或 mobile")
    
    target_dir = DESKTOP_BANNER_DIR if device == "desktop" else MOBILE_BANNER_DIR
    image_path = target_dir / filename
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="图片不存在")
    
    # 生成或获取缩略图
    thumb_path = generate_thumbnail(image_path, device)
    
    return FileResponse(
        thumb_path,
        media_type="image/jpeg",
        headers={"Cache-Control": "public, max-age=86400"}  # 缓存1天
    )


@router.post("/upload/{device}")
async def upload_banner(
    device: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传 banner 图片"""
    if device not in ["desktop", "mobile"]:
        raise HTTPException(status_code=400, detail="设备类型必须是 desktop 或 mobile")
    
    # 验证文件类型
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/avif"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持 JPG/PNG/GIF/WebP/AVIF 格式")
    
    target_dir = DESKTOP_BANNER_DIR if device == "desktop" else MOBILE_BANNER_DIR
    
    # 保存文件
    file_path = target_dir / file.filename
    try:
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # 预生成缩略图
        generate_thumbnail(file_path, device)
        
        return {"message": "上传成功", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.delete("/{device}/{filename}")
async def delete_banner(
    device: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """删除 banner 图片"""
    if device not in ["desktop", "mobile"]:
        raise HTTPException(status_code=400, detail="设备类型必须是 desktop 或 mobile")
    
    target_dir = DESKTOP_BANNER_DIR if device == "desktop" else MOBILE_BANNER_DIR
    file_path = target_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        file_path.unlink()
        
        # 同时删除缩略图
        thumb_path = THUMBNAIL_DIR / f"{device}_{filename}"
        if thumb_path.exists():
            thumb_path.unlink()
        
        return {"message": "删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
