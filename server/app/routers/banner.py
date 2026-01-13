# Banner 管理接口
import os
import json
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/banner", tags=["banner"])

# Banner 图片存储路径
CLIENT_PUBLIC = Path(__file__).parent.parent.parent.parent / "client" / "public"
DESKTOP_BANNER_DIR = CLIENT_PUBLIC / "assets" / "desktop-banner"
MOBILE_BANNER_DIR = CLIENT_PUBLIC / "assets" / "mobile-banner"

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


@router.get("", response_model=BannerListResponse)
async def get_banners(current_user: User = Depends(get_current_user)):
    """获取所有 banner 图片列表"""
    return BannerListResponse(
        desktop=get_banner_images(DESKTOP_BANNER_DIR),
        mobile=get_banner_images(MOBILE_BANNER_DIR)
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
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
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
        return {"message": "删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
