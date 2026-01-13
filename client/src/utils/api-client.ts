/**
 * API 客户端 - 用于从 FastAPI 后端获取数据
 */

// SSR 服务端需要使用完整 URL，客户端使用相对路径
// 生产环境：前后端同源部署，使用相对路径
// 开发环境：前端 4321 端口，后端 8000 端口，需要完整 URL
const isDev = import.meta.env?.DEV ?? (typeof process !== 'undefined' && process.env.NODE_ENV === 'development');
const isSSR = typeof window === 'undefined';

// SSR 构建时需要完整 URL，客户端可以用相对路径
export const API_BASE = isSSR
    ? (process.env.API_URL || 'http://localhost:8000')  // SSR/构建时
    : (isDev
        ? `http://${window.location.hostname}:8000`    // 客户端开发环境：动态获取当前 IP/域名
        : '');                                         // 客户端生产环境：相对路径

export interface ApiPost {
    id: number;
    title: string;
    slug: string;
    content: string;
    summary: string | null;
    cover_image: string | null;
    is_published: boolean;
    is_pinned: boolean;
    view_count: number;
    created_at: string;
    updated_at: string;
    category: ApiCategory | null;
    tags: ApiTag[];
    author: {
        id: number;
        username: string;
    };
    comment_count: number;
}

export interface ApiPostList {
    id: number;
    title: string;
    slug: string;
    summary: string | null;
    cover_image: string | null;
    is_published: boolean;
    is_pinned: boolean;
    view_count: number;
    created_at: string;
    category: ApiCategory | null;
    tags: ApiTag[];
    comment_count: number;
}

export interface ApiCategory {
    id: number;
    name: string;
    slug: string;
    description: string | null;
    post_count: number;
}

export interface ApiTag {
    id: number;
    name: string;
    slug: string;
    post_count: number;
}

export interface ApiComment {
    id: number;
    nickname: string;
    email: string | null;
    website: string | null;
    content: string;
    is_approved: boolean;
    created_at: string;
    post_id: number;
    parent_id: number | null;
    replies: ApiComment[];
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

export interface ApiStats {
    posts: number;
    categories: number;
    tags: number;
    comments: number;
    views: number;
}

/**
 * 获取文章列表
 */
export async function fetchPosts(
    page: number = 1,
    pageSize: number = 10,
    category?: string,
    tag?: string
): Promise<PaginatedResponse<ApiPostList>> {
    const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
    });
    if (category) params.append('category', category);
    if (tag) params.append('tag', tag);

    const res = await fetch(`${API_BASE}/api/posts?${params}`);
    if (!res.ok) throw new Error('Failed to fetch posts');
    return res.json();
}

/**
 * 获取单篇文章详情
 */
export async function fetchPost(slug: string): Promise<ApiPost> {
    const res = await fetch(`${API_BASE}/api/posts/${slug}`);
    if (!res.ok) {
        if (res.status === 404) throw new Error('Post not found');
        throw new Error('Failed to fetch post');
    }
    return res.json();
}

/**
 * 获取分类列表
 */
export async function fetchCategories(): Promise<ApiCategory[]> {
    const res = await fetch(`${API_BASE}/api/categories`);
    if (!res.ok) throw new Error('Failed to fetch categories');
    return res.json();
}

/**
 * 获取标签列表
 */
export async function fetchTags(): Promise<ApiTag[]> {
    const res = await fetch(`${API_BASE}/api/tags`);
    if (!res.ok) throw new Error('Failed to fetch tags');
    return res.json();
}

/**
 * 获取文章评论
 */
export async function fetchComments(slug: string): Promise<ApiComment[]> {
    const res = await fetch(`${API_BASE}/api/posts/${slug}/comments`);
    if (!res.ok) throw new Error('Failed to fetch comments');
    return res.json();
}

/**
 * 提交评论
 */
export async function submitComment(data: {
    post_id: number;
    nickname: string;
    email?: string;
    website?: string;
    content: string;
    parent_id?: number;
}): Promise<ApiComment> {
    const res = await fetch(`${API_BASE}/api/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to submit comment');
    return res.json();
}

/**
 * 获取博客统计
 */
export async function fetchStats(): Promise<ApiStats> {
    const res = await fetch(`${API_BASE}/api/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
}
