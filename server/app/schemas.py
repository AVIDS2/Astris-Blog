from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============ 用户 ============
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    avatar: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# ============ 分类 ============
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    post_count: int = 0
    
    class Config:
        from_attributes = True


# ============ 标签 ============
class TagBase(BaseModel):
    name: str
    slug: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    post_count: int = 0
    
    class Config:
        from_attributes = True


# ============ 文章 ============
class PostBase(BaseModel):
    title: str
    slug: str
    content: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    is_published: bool = False
    is_pinned: bool = False


class PostCreate(PostBase):
    category_id: Optional[int] = None
    tag_ids: List[int] = []


class PostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    is_published: Optional[bool] = None
    is_pinned: Optional[bool] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class PostResponse(PostBase):
    id: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    author: UserResponse
    comment_count: int = 0
    
    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """文章列表响应（不包含完整内容）"""
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    is_published: bool
    is_pinned: bool
    view_count: int
    created_at: datetime
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    comment_count: int = 0
    
    class Config:
        from_attributes = True


# ============ 评论 ============
class CommentBase(BaseModel):
    nickname: str
    email: Optional[str] = None
    website: Optional[str] = None
    content: str


class CommentCreate(CommentBase):
    post_id: int
    parent_id: Optional[int] = None


class CommentResponse(CommentBase):
    id: int
    is_approved: bool
    created_at: datetime
    post_id: int
    parent_id: Optional[int] = None
    replies: List["CommentResponse"] = []
    
    class Config:
        from_attributes = True


# ============ 分页 ============
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int
