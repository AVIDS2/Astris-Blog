"""搜索 API 路由"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from app.database import get_db
from app.models import Post, Category, Tag


router = APIRouter()


class SearchResultItem(BaseModel):
    """搜索结果项"""
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    excerpt: str  # 匹配内容的摘要片段
    cover_image: Optional[str] = None
    category_name: Optional[str] = None
    tags: List[str] = []
    created_at: str
    url: str


class SearchResponse(BaseModel):
    """搜索响应"""
    query: str
    total: int
    results: List[SearchResultItem]


def extract_excerpt(content: str, keyword: str, max_length: int = 150) -> str:
    """从内容中提取包含关键词的摘要片段"""
    keyword_lower = keyword.lower()
    content_lower = content.lower()
    
    # 查找关键词位置
    pos = content_lower.find(keyword_lower)
    
    if pos == -1:
        # 如果没找到关键词，返回开头部分
        excerpt = content[:max_length]
    else:
        # 计算摘要的起始和结束位置
        start = max(0, pos - 50)
        end = min(len(content), pos + len(keyword) + 100)
        
        # 尝试从单词边界开始
        if start > 0:
            # 找到最近的空格或换行
            space_pos = content.rfind(' ', 0, start + 20)
            if space_pos > start - 30:
                start = space_pos + 1
        
        excerpt = content[start:end]
        
        # 添加省略号
        if start > 0:
            excerpt = '...' + excerpt
        if end < len(content):
            excerpt = excerpt + '...'
    
    # 高亮关键词（用 <mark> 标签包裹）
    import re
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    excerpt = pattern.sub(f'<mark>{keyword}</mark>', excerpt)
    
    return excerpt


@router.get("/search", response_model=SearchResponse)
async def search_posts(
    q: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="返回结果数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    搜索已发布的文章
    
    搜索范围包括：标题、摘要、内容、分类名称、标签名称
    """
    keyword = q.strip()
    
    if not keyword:
        return SearchResponse(query=keyword, total=0, results=[])
    
    # 构建搜索查询 - 在标题、摘要、内容中搜索
    query = select(Post).where(
        Post.is_published == True,
        or_(
            Post.title.ilike(f"%{keyword}%"),
            Post.summary.ilike(f"%{keyword}%"),
            Post.content.ilike(f"%{keyword}%"),
        )
    ).options(
        selectinload(Post.category),
        selectinload(Post.tags),
    ).order_by(
        # 标题匹配优先级最高
        Post.title.ilike(f"%{keyword}%").desc(),
        Post.created_at.desc()
    ).limit(limit)
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    # 构建搜索结果
    search_results = []
    for post in posts:
        # 提取包含关键词的摘要
        if keyword.lower() in post.title.lower():
            excerpt = post.summary or extract_excerpt(post.content, keyword)
        elif post.summary and keyword.lower() in post.summary.lower():
            excerpt = extract_excerpt(post.summary, keyword)
        else:
            excerpt = extract_excerpt(post.content, keyword)
        
        search_results.append(SearchResultItem(
            id=post.id,
            title=post.title,
            slug=post.slug,
            summary=post.summary,
            excerpt=excerpt,
            cover_image=post.cover_image,
            category_name=post.category.name if post.category else None,
            tags=[tag.name for tag in post.tags],
            created_at=post.created_at.isoformat(),
            url=f"/posts/{post.slug}/"
        ))
    
    return SearchResponse(
        query=keyword,
        total=len(search_results),
        results=search_results
    )
