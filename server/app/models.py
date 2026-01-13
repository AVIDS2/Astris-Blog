from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


# 文章-标签 多对多关联表
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """用户/管理员"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关联
    posts: Mapped[List["Post"]] = relationship(back_populates="author")


class Category(Base):
    """文章分类"""
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # 关联
    posts: Mapped[List["Post"]] = relationship(back_populates="category")


class Tag(Base):
    """标签"""
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    
    # 关联
    posts: Mapped[List["Post"]] = relationship(secondary=post_tags, back_populates="tags")


class Post(Base):
    """文章"""
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    content: Mapped[str] = mapped_column(Text)  # Markdown 内容
    summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cover_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # 关联
    category: Mapped[Optional["Category"]] = relationship(back_populates="posts")
    author: Mapped["User"] = relationship(back_populates="posts")
    tags: Mapped[List["Tag"]] = relationship(secondary=post_tags, back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    """评论"""
    __tablename__ = "comments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)  # 需要审核
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 外键
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comments.id"), nullable=True)
    
    # 关联
    post: Mapped["Post"] = relationship(back_populates="comments")
    parent: Mapped[Optional["Comment"]] = relationship(remote_side=[id], backref="replies")


class Tool(Base):
    """收藏的实用工具"""
    __tablename__ = "tools"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))  # 工具名称
    url: Mapped[str] = mapped_column(String(500))  # 工具链接
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # 简介
    icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # 图标 URL
    category: Mapped[str] = mapped_column(String(50), default="其他")  # 分类
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # 排序
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否显示
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Album(Base):
    """相册"""
    __tablename__ = "albums"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))  # 相册名称
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # 描述
    cover: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # 封面图
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # 排序
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否显示
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关联
    photos: Mapped[List["Photo"]] = relationship(back_populates="album", cascade="all, delete-orphan")


class Photo(Base):
    """照片"""
    __tablename__ = "photos"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(500))  # 照片 URL
    thumbnail: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # 缩略图
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # 标题
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # 描述
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # 排序
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 外键
    album_id: Mapped[int] = mapped_column(ForeignKey("albums.id", ondelete="CASCADE"))
    
    # 关联
    album: Mapped["Album"] = relationship(back_populates="photos")


class Friend(Base):
    """友情链接"""
    __tablename__ = "friends"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))  # 友链名称
    url: Mapped[str] = mapped_column(String(500))  # 链接地址
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # 头像
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # 描述
    tags: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # 标签，逗号分隔
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # 排序
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否显示
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

