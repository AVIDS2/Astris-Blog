from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Friend
from app.routers.admin import get_current_active_user

router = APIRouter()


# Schemas
class FriendBase(BaseModel):
    name: str
    url: str
    avatar: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    sort_order: int = 0
    is_visible: bool = True


class FriendCreate(FriendBase):
    pass


class FriendUpdate(FriendBase):
    pass


class FriendResponse(FriendBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 公开接口 - 获取所有可见友链
@router.get("/friends", response_model=List[FriendResponse])
async def get_friends(db: AsyncSession = Depends(get_db)):
    """获取所有可见的友情链接"""
    result = await db.execute(
        select(Friend)
        .where(Friend.is_visible == True)
        .order_by(Friend.sort_order.asc(), Friend.created_at.desc())
    )
    friends = result.scalars().all()
    return friends


# 管理接口 - 获取所有友链（包括隐藏的）
@router.get("/admin/friends", response_model=List[FriendResponse])
async def admin_get_friends(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """管理员获取所有友情链接"""
    result = await db.execute(
        select(Friend).order_by(Friend.sort_order.asc(), Friend.created_at.desc())
    )
    friends = result.scalars().all()
    return friends


# 管理接口 - 创建友链
@router.post("/admin/friends", response_model=FriendResponse)
async def create_friend(
    friend: FriendCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建友情链接"""
    new_friend = Friend(
        name=friend.name,
        url=friend.url,
        avatar=friend.avatar,
        description=friend.description,
        tags=friend.tags,
        sort_order=friend.sort_order,
        is_visible=friend.is_visible
    )
    db.add(new_friend)
    await db.commit()
    await db.refresh(new_friend)
    return new_friend


# 管理接口 - 更新友链
@router.put("/admin/friends/{friend_id}", response_model=FriendResponse)
async def update_friend(
    friend_id: int,
    friend: FriendUpdate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新友情链接"""
    result = await db.execute(select(Friend).where(Friend.id == friend_id))
    db_friend = result.scalar_one_or_none()
    
    if not db_friend:
        raise HTTPException(status_code=404, detail="友链不存在")
    
    db_friend.name = friend.name
    db_friend.url = friend.url
    db_friend.avatar = friend.avatar
    db_friend.description = friend.description
    db_friend.tags = friend.tags
    db_friend.sort_order = friend.sort_order
    db_friend.is_visible = friend.is_visible
    
    await db.commit()
    await db.refresh(db_friend)
    return db_friend


# 管理接口 - 删除友链
@router.delete("/admin/friends/{friend_id}")
async def delete_friend(
    friend_id: int,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除友情链接"""
    result = await db.execute(select(Friend).where(Friend.id == friend_id))
    db_friend = result.scalar_one_or_none()
    
    if not db_friend:
        raise HTTPException(status_code=404, detail="友链不存在")
    
    await db.delete(db_friend)
    await db.commit()
    return {"message": "删除成功"}
