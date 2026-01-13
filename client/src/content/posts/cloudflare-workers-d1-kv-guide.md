---
title: Cloudflare Workers + D1 + KV 部署指南
published: 2026-01-13
description: Cloudflare Serverless全家桶的部署方法和免费套餐限制说明
tags: [Cloudflare, Serverless, 部署教程, 免费]
category: 技术
image: https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200
draft: false
---

Cloudflare的Serverless服务对个人开发者很友好——免费额度足够日常使用，全球边缘节点速度快，部署简单。这里记录一下Workers + D1 + KV的部署方法和需要注意的限制。

## 服务定位

| 服务 | 用途 | 类比 |
|------|------|------|
| Workers | 边缘计算运行时 | AWS Lambda，但运行在CDN节点 |
| D1 | 边缘SQLite数据库 | PlanetScale的轻量版 |
| KV | 键值存储 | Redis，但是最终一致性 |

![Cloudflare边缘网络](https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800)

## 免费套餐限制（2025年数据）

### Workers

| 限制项 | 免费套餐 | 付费套餐 |
|--------|---------|---------|
| CPU时间 | 10ms/请求 | 5分钟 |
| 内存 | 128MB | 128MB |
| 脚本大小 | 3MB | 10MB |
| 子请求 | 50个/请求 | 1000个 |

10ms听起来很短，但对于简单的API代理、数据处理来说足够了。

### D1

| 限制项 | 免费套餐 | 付费套餐 |
|--------|---------|---------|
| 数据库数量 | 10个 | 50,000个 |
| 单库大小 | 500MB | 10GB |
| 总存储 | 5GB | 1TB |
| 每次请求查询数 | 50次 | 1000次 |

**注意**：D1免费套餐限制从2025年2月10日开始执行。D1是单线程的，一次处理一个查询，大批量写入需要分批操作。

### KV

| 限制项 | 免费套餐 | 付费套餐 |
|--------|---------|---------|
| 读取 | 10万次/天 | 无限 |
| 写入（不同键） | 1000次/天 | 无限 |
| 写入（相同键） | 1次/秒 | 1次/秒 |
| 存储 | 1GB | 无限 |

**重点**：同一个键每秒只能写入1次。做计数器的话需要注意这个限制。

## 部署步骤

### 1. 安装Wrangler CLI

```bash
npm install -g wrangler
wrangler login
```

### 2. 创建项目

```bash
npm create cloudflare@latest my-api
cd my-api
```

### 3. 创建D1数据库

```bash
npx wrangler d1 create my-database
```

在`wrangler.toml`中添加配置：

```toml
[[d1_databases]]
binding = "DB"
database_name = "my-database"
database_id = "你的数据库ID"
```

### 4. 初始化表结构

```sql
-- schema.sql
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

```bash
npx wrangler d1 execute my-database --file=./schema.sql
```

### 5. 编写Worker

```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    if (url.pathname === '/api/users') {
      const { results } = await env.DB.prepare(
        'SELECT * FROM users LIMIT 10'
      ).all();
      
      return Response.json(results);
    }
    
    return new Response('Hello from Cloudflare Workers');
  },
};
```

### 6. 部署

```bash
wrangler deploy
```

![部署成功](https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800)

## 常用技巧

### KV缓存模式

```javascript
let data = await env.KV.get('cache_key', 'json');

if (!data) {
  const { results } = await env.DB.prepare('SELECT...').all();
  data = results;
  await env.KV.put('cache_key', JSON.stringify(data), {
    expirationTtl: 1800 // 30分钟过期
  });
}

return Response.json(data);
```

### D1批量操作

```javascript
// 避免循环单条插入
const stmt = env.DB.prepare('INSERT INTO users (name) VALUES (?)');
await env.DB.batch(names.map(n => stmt.bind(n)));
```

### 避免KV同键限速

```javascript
// 使用细粒度的键名
const today = new Date().toISOString().split('T')[0];
const key = `pageviews:${postId}:${today}`;
```

## 什么时候该付费

- 日活超过10万
- 数据库超过500MB
- 需要实时一致性（考虑Durable Objects）

---

*Cloudflare的文档写得不错，遇到问题可以直接查官方文档。*
