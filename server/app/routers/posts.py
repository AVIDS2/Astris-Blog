from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Post, Category, Tag, Comment
from app.schemas import (
    PostResponse, PostListResponse, CategoryResponse, TagResponse,
    CommentResponse, CommentCreate, PaginatedResponse
)

router = APIRouter()


@router.get("/posts", response_model=PaginatedResponse)
async def get_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=500),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取已发布的文章列表"""
    query = select(Post).where(Post.is_published == True).options(
        selectinload(Post.category),
        selectinload(Post.tags),
        selectinload(Post.author),
    ).order_by(Post.is_pinned.desc(), Post.created_at.desc())
    
    # 按分类筛选
    if category:
        query = query.join(Post.category).where(Category.slug == category)
    
    # 按标签筛选
    if tag:
        query = query.join(Post.tags).where(Tag.slug == tag)
    
    # 统计总数（需要包含相同的筛选条件）
    count_query = select(func.count()).select_from(Post).where(Post.is_published == True)
    if category:
        count_query = count_query.join(Post.category).where(Category.slug == category)
    if tag:
        count_query = count_query.join(Post.tags).where(Tag.slug == tag)
        
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    posts = result.scalars().all()
    
    # 获取评论数
    items = []
    for post in posts:
        comment_count = await db.execute(
            select(func.count()).select_from(Comment).where(
                Comment.post_id == post.id,
                Comment.is_approved == True
            )
        )
        post_dict = {
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "summary": post.summary,
            "cover_image": post.cover_image,
            "is_published": post.is_published,
            "is_pinned": post.is_pinned,
            "view_count": post.view_count,
            "created_at": post.created_at,
            "category": post.category,
            "tags": post.tags,
            "comment_count": comment_count.scalar()
        }
        items.append(PostListResponse(**post_dict))
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/posts/{slug}", response_model=PostResponse)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    """获取单篇文章详情"""
    result = await db.execute(
        select(Post).where(Post.slug == slug, Post.is_published == True).options(
            selectinload(Post.category),
            selectinload(Post.tags),
            selectinload(Post.author),
        )
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 增加浏览量
    post.view_count += 1
    await db.commit()
    
    # 获取评论数
    comment_count = await db.execute(
        select(func.count()).select_from(Comment).where(
            Comment.post_id == post.id,
            Comment.is_approved == True
        )
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


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """获取所有分类"""
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    
    items = []
    for cat in categories:
        count = await db.execute(
            select(func.count()).select_from(Post).where(
                Post.category_id == cat.id,
                Post.is_published == True
            )
        )
        items.append(CategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            post_count=count.scalar()
        ))
    return items


@router.get("/tags", response_model=List[TagResponse])
async def get_tags(db: AsyncSession = Depends(get_db)):
    """获取所有标签"""
    result = await db.execute(select(Tag))
    tags = result.scalars().all()
    
    items = []
    for tag in tags:
        count = await db.execute(
            select(func.count()).select_from(Post).join(Post.tags).where(
                Tag.id == tag.id,
                Post.is_published == True
            )
        )
        items.append(TagResponse(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
            post_count=count.scalar()
        ))
    return items


@router.get("/posts/{slug}/comments", response_model=List[CommentResponse])
async def get_comments(slug: str, db: AsyncSession = Depends(get_db)):
    """获取文章的已审核评论"""
    # 先获取文章
    post_result = await db.execute(select(Post).where(Post.slug == slug))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 获取顶级评论（没有 parent_id 的）
    result = await db.execute(
        select(Comment).where(
            Comment.post_id == post.id,
            Comment.is_approved == True,
            Comment.parent_id == None
        ).order_by(Comment.created_at.desc())
    )
    comments = result.scalars().all()
    
    # 递归获取回复
    async def get_replies(comment_id: int):
        result = await db.execute(
            select(Comment).where(
                Comment.parent_id == comment_id,
                Comment.is_approved == True
            ).order_by(Comment.created_at.asc())
        )
        replies = result.scalars().all()
        items = []
        for reply in replies:
            reply_dict = CommentResponse(
                id=reply.id,
                nickname=reply.nickname,
                email=reply.email,
                website=reply.website,
                content=reply.content,
                is_approved=reply.is_approved,
                created_at=reply.created_at,
                post_id=reply.post_id,
                parent_id=reply.parent_id,
                replies=await get_replies(reply.id)
            )
            items.append(reply_dict)
        return items
    
    result_comments = []
    for comment in comments:
        comment_dict = CommentResponse(
            id=comment.id,
            nickname=comment.nickname,
            email=comment.email,
            website=comment.website,
            content=comment.content,
            is_approved=comment.is_approved,
            created_at=comment.created_at,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            replies=await get_replies(comment.id)
        )
        result_comments.append(comment_dict)
    
    return result_comments


@router.post("/comments", response_model=CommentResponse)
async def create_comment(comment: CommentCreate, db: AsyncSession = Depends(get_db)):
    """提交评论（需要审核）"""
    # 验证文章存在
    post_result = await db.execute(select(Post).where(Post.id == comment.post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 验证父评论存在（如果有）
    if comment.parent_id:
        parent_result = await db.execute(select(Comment).where(Comment.id == comment.parent_id))
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=404, detail="回复的评论不存在")
    
    new_comment = Comment(
        nickname=comment.nickname,
        email=comment.email,
        website=comment.website,
        content=comment.content,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        is_approved=False  # 默认需要审核
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    
    return CommentResponse(
        id=new_comment.id,
        nickname=new_comment.nickname,
        email=new_comment.email,
        website=new_comment.website,
        content=new_comment.content,
        is_approved=new_comment.is_approved,
        created_at=new_comment.created_at,
        post_id=new_comment.post_id,
        parent_id=new_comment.parent_id,
        replies=[]
    )


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """获取博客统计信息"""
    posts_count = await db.execute(
        select(func.count()).select_from(Post).where(Post.is_published == True)
    )
    categories_count = await db.execute(select(func.count()).select_from(Category))
    tags_count = await db.execute(select(func.count()).select_from(Tag))
    comments_count = await db.execute(
        select(func.count()).select_from(Comment).where(Comment.is_approved == True)
    )
    total_views = await db.execute(
        select(func.sum(Post.view_count)).where(Post.is_published == True)
    )
    
    return {
        "posts": posts_count.scalar(),
        "categories": categories_count.scalar(),
        "tags": tags_count.scalar(),
        "comments": comments_count.scalar(),
        "views": total_views.scalar() or 0
    }
