# 🚀 博客部署指南

## 📋 部署前准备

### 1. 确保服务器已安装
- Docker (20.10+)
- Docker Compose (v2+)

### 2. 创建环境变量文件

在项目根目录创建 `.env` 文件（参考 `.env.example`）：

```bash
# 生成随机密钥
SECRET_KEY=$(openssl rand -hex 32)

# 创建 .env 文件
cat > .env << EOF
SECRET_KEY=$SECRET_KEY
ADMIN_USERNAME=你的用户名
ADMIN_PASSWORD=你的强密码
CORS_ORIGINS=https://你的域名.com
EOF
```

⚠️ **重要**：`.env` 文件包含敏感信息，请勿提交到 Git！

---

## 🐳 Docker 部署

### 方式一：使用 docker-compose（推荐）

```bash
# 1. 上传项目文件到服务器
scp -r my_blog/ user@server:/path/to/

# 2. 进入项目目录
cd /path/to/my_blog

# 3. 创建 .env 文件（见上方说明）

# 4. 创建数据目录
mkdir -p data uploads

# 5. 构建并启动
docker-compose up -d --build

# 6. 查看日志
docker-compose logs -f

# 7. 查看服务状态
docker-compose ps
```

### 方式二：手动构建

```bash
# 构建镜像
docker build -t dwill-blog .

# 运行容器
docker run -d \
  --name dwill-blog \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/uploads:/app/uploads \
  -e SECRET_KEY=你的密钥 \
  -e ADMIN_USERNAME=你的用户名 \
  -e ADMIN_PASSWORD=你的密码 \
  -e CORS_ORIGINS=https://你的域名.com \
  dwill-blog
```

---

## 🌐 反向代理配置

### Caddy（推荐）

```caddyfile
你的域名.com {
    reverse_proxy localhost:8000
}
```

```bash
caddy reload
```

### Nginx

```nginx
server {
    listen 80;
    server_name 你的域名.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📁 数据持久化

| 容器路径 | 主机路径 | 说明 |
|---------|---------|------|
| `/app/data` | `./data` | SQLite 数据库 |
| `/app/uploads` | `./uploads` | 上传的图片文件 |

---

## 🔧 常用运维命令

```bash
# 查看容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f blog

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新部署（拉取代码后）
docker-compose up -d --build

# 进入容器调试
docker-compose exec blog bash

# 备份数据库
cp ./data/blog.db ./data/blog.db.backup.$(date +%Y%m%d)

# 备份上传文件
tar -czvf uploads_backup_$(date +%Y%m%d).tar.gz ./uploads
```

---

## 🔒 安全建议

1. **修改默认密码**：首次登录管理后台后立即修改密码
2. **使用强密钥**：`SECRET_KEY` 应使用 `openssl rand -hex 32` 生成
3. **限制 CORS**：`CORS_ORIGINS` 只允许你的域名
4. **启用 HTTPS**：确保反向代理已配置 SSL 证书
5. **定期备份**：备份 `./data` 和 `./uploads` 目录
6. **更新依赖**：定期更新 Docker 镜像和依赖包

---

## 🐛 常见问题

### Q: 图片无法显示
检查目录权限：
```bash
chmod -R 755 ./uploads
```

### Q: 数据库锁定错误
重启容器：
```bash
docker-compose restart
```

### Q: 构建失败（内存不足）
增加 Docker 内存限制或使用 swap：
```bash
# 临时增加 swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Q: 端口被占用
修改 docker-compose.yml 中的端口映射：
```yaml
ports:
  - "你的端口:8000"
```

### Q: 首次访问很慢
这是正常的，SSR 模式首次请求需要渲染。后续访问会更快。

---

## 📊 健康检查

部署完成后，访问以下地址确认服务正常：

- 前端首页：`https://你的域名.com/`
- API 健康检查：`https://你的域名.com/api/health`
- 管理后台：`https://你的域名.com/admin/`

---

## 🔄 更新部署

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建并启动
docker-compose up -d --build

# 3. 查看日志确认启动成功
docker-compose logs -f
```
