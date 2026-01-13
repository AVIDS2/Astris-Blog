"""
工具收藏 API
公开接口 + 管理接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Tool
from app.auth import get_current_user

router = APIRouter(prefix="/api/tools", tags=["工具收藏"])


# ========== Pydantic 模型 ==========

class ToolCreate(BaseModel):
    name: str
    url: str
    description: Optional[str] = None
    icon: Optional[str] = None
    category: str = "其他"
    sort_order: int = 0
    is_visible: bool = True


class ToolUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    sort_order: Optional[int] = None
    is_visible: Optional[bool] = None


class ToolResponse(BaseModel):
    id: int
    name: str
    url: str
    description: Optional[str]
    icon: Optional[str]
    category: str
    sort_order: int
    is_visible: bool

    class Config:
        from_attributes = True


# ========== 公开接口 ==========

@router.get("")
async def get_tools(db: AsyncSession = Depends(get_db)):
    """获取所有可见的工具列表（按分类分组）"""
    result = await db.execute(
        select(Tool)
        .where(Tool.is_visible == True)
        .order_by(Tool.category, Tool.sort_order)
    )
    tools = result.scalars().all()
    
    # 按分类分组
    grouped = {}
    for tool in tools:
        if tool.category not in grouped:
            grouped[tool.category] = []
        grouped[tool.category].append(ToolResponse.model_validate(tool))
    
    return grouped


# ========== 管理接口 ==========

@router.get("/admin/all")
async def get_all_tools(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """获取所有工具（包括隐藏的）"""
    result = await db.execute(
        select(Tool).order_by(Tool.category, Tool.sort_order)
    )
    tools = result.scalars().all()
    return [ToolResponse.model_validate(t) for t in tools]


@router.post("/admin")
async def create_tool(
    tool: ToolCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """创建新工具"""
    new_tool = Tool(**tool.model_dump())
    db.add(new_tool)
    await db.commit()
    await db.refresh(new_tool)
    return ToolResponse.model_validate(new_tool)


@router.put("/admin/{tool_id}")
async def update_tool(
    tool_id: int,
    tool: ToolUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """更新工具"""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    db_tool = result.scalar_one_or_none()
    
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    for key, value in tool.model_dump(exclude_unset=True).items():
        setattr(db_tool, key, value)
    
    await db.commit()
    await db.refresh(db_tool)
    return ToolResponse.model_validate(db_tool)


@router.delete("/admin/{tool_id}")
async def delete_tool(
    tool_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """删除工具"""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    db_tool = result.scalar_one_or_none()
    
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    await db.delete(db_tool)
    await db.commit()
    return {"message": "Tool deleted"}
