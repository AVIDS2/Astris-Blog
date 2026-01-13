from datetime import timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
import os
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import User, Post, Category, Tag, Comment
from app.schemas import (
    Token, UserResponse, PostCreate, PostUpdate, PostResponse,
    CategoryCreate, CategoryResponse, TagCreate, TagResponse,
    CommentResponse
)
from app.auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_active_user
)
from app.config import get_settings

settings = get_settings()
router = APIRouter()


# ============ 认证 ============
@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """管理员登录"""
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)


@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user


# ============ 文章管理 ============
@router.get("/posts", response_model=List[PostResponse])
async def admin_get_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有文章（包括未发布）"""
    result = await db.execute(
        select(Post).options(
            selectinload(Post.category),
            selectinload(Post.tags),
            selectinload(Post.author),
        ).order_by(Post.created_at.desc())
    )
    posts = result.scalars().all()
    
    items = []
    for post in posts:
        comment_count = await db.execute(
            select(func.count()).select_from(Comment).where(Comment.post_id == post.id)
        )
        items.append(PostResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            content=post.content,
            summary=post.summary,
            cover_image=post.cover_image,
            is_published=post.is_published,
            is_pinned=post.is_pinned,
            view_count=post.view_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
            category=post.category,
            tags=post.tags,
            author=post.author,
            comment_count=comment_count.scalar()
        ))
    return items


@router.post("/posts", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建文章"""
    # 检查 slug 是否重复
    existing = await db.execute(select(Post).where(Post.slug == post.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="文章 slug 已存在")
    
    # 获取标签
    tags = []
    if post.tag_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(post.tag_ids)))
        tags = result.scalars().all()
    
    new_post = Post(
        title=post.title,
        slug=post.slug,
        content=post.content,
        summary=post.summary,
        cover_image=post.cover_image,
        is_published=post.is_published,
        is_pinned=post.is_pinned,
        category_id=post.category_id,
        author_id=current_user.id,
        tags=tags
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    # 重新加载关联
    result = await db.execute(
        select(Post).where(Post.id == new_post.id).options(
            selectinload(Post.category),
            selectinload(Post.tags),
            selectinload(Post.author),
        )
    )
    new_post = result.scalar_one()
    
    return PostResponse(
        id=new_post.id,
        title=new_post.title,
        slug=new_post.slug,
        content=new_post.content,
        summary=new_post.summary,
        cover_image=new_post.cover_image,
        is_published=new_post.is_published,
        is_pinned=new_post.is_pinned,
        view_count=new_post.view_count,
        created_at=new_post.created_at,
        updated_at=new_post.updated_at,
        category=new_post.category,
        tags=new_post.tags,
        author=new_post.author,
        comment_count=0
    )


@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新文章"""
    result = await db.execute(
        select(Post).where(Post.id == post_id).options(
            selectinload(Post.category),
            selectinload(Post.tags),
            selectinload(Post.author),
        )
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 更新字段
    update_data = post_update.model_dump(exclude_unset=True)
    
    # 处理标签
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
            post.tags = result.scalars().all()
    
    for key, value in update_data.items():
        setattr(post, key, value)
    
    await db.commit()
    await db.refresh(post)
    
    comment_count = await db.execute(
        select(func.count()).select_from(Comment).where(Comment.post_id == post.id)
    )
    
    return PostResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        content=post.content,
        summary=post.summary,
        cover_image=post.cover_image,
        is_published=post.is_published,
        is_pinned=post.is_pinned,
        view_count=post.view_count,
        created_at=post.created_at,
        updated_at=post.updated_at,
        category=post.category,
        tags=post.tags,
        author=post.author,
        comment_count=comment_count.scalar()
    )


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除文章"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    await db.delete(post)
    await db.commit()
    return {"message": "文章已删除"}


# ============ 分类管理 ============
@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建分类"""
    existing = await db.execute(select(Category).where(Category.slug == category.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="分类 slug 已存在")
    
    new_category = Category(**category.model_dump())
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    
    return CategoryResponse(
        id=new_category.id,
        name=new_category.name,
        slug=new_category.slug,
        description=new_category.description,
        post_count=0
    )


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除分类"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    await db.delete(category)
    await db.commit()
    return {"message": "分类已删除"}


# ============ 标签管理 ============
@router.post("/tags", response_model=TagResponse)
async def create_tag(
    tag: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建标签"""
    existing = await db.execute(select(Tag).where(Tag.slug == tag.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="标签 slug 已存在")
    
    new_tag = Tag(**tag.model_dump())
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    
    return TagResponse(id=new_tag.id, name=new_tag.name, slug=new_tag.slug, post_count=0)


@router.delete("/tags/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除标签"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    await db.delete(tag)
    await db.commit()
    return {"message": "标签已删除"}


# ============ 评论管理 ============
@router.get("/comments")
async def admin_get_comments(
    approved: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有评论（包含文章信息）"""
    query = select(Comment).options(selectinload(Comment.post)).order_by(Comment.created_at.desc())
    if approved is not None:
        query = query.where(Comment.is_approved == approved)
    
    result = await db.execute(query)
    comments = result.scalars().all()
    
    return [{
        "id": c.id,
        "nickname": c.nickname,
        "email": c.email,
        "website": c.website,
        "content": c.content,
        "is_approved": c.is_approved,
        "created_at": c.created_at.isoformat(),
        "post_id": c.post_id,
        "post_title": c.post.title if c.post else "已删除的文章",
        "post_slug": c.post.slug if c.post else None,
        "parent_id": c.parent_id,
    } for c in comments]


@router.put("/comments/{comment_id}/approve")
async def approve_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """审核通过评论"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    comment.is_approved = True
    await db.commit()
    return {"message": "评论已通过审核"}


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除评论"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    await db.delete(comment)
    await db.commit()
    return {"message": "评论已删除"}
# ============= 图片管理 =============
@router.post("/upload", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """编辑器内图片上传"""
    # 确保目录存在
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "photos")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 检查扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        raise HTTPException(status_code=400, detail="不支持的图片格式")
    
    # 生成唯一文件名
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)
    
    # 保存文件
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
    # 返回 URL
    return {"url": f"/uploads/photos/{filename}"}
