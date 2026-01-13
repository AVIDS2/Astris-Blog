# 🚀 D.Will Blog 部署指南

## 环境信息
- **主域名**: `dwill.top` (Cloudflare 转发)
- **子域名**: `blog.dwill.top:7777` (Caddy 反代)
- **反向代理**: Caddy
- **容器宿主机端口**: `9527` (映射到容器内 8000)
- **项目根目录**: `C:\Users\SERVER\Desktop\zt\my_blog`

---

## 第一步：上传项目

将整个 `my_blog` 文件夹复制到服务器的 `C:\Users\SERVER\Desktop\zt\` 目录下。
确保包含以下重要文件：
- `Dockerfile`
- `docker-compose.yml`
- `server/`
- `client/`

---

## 第二步：配置环境变量

在项目根目录下创建 `.env` 文件：

```bash
cd C:\Users\SERVER\Desktop\zt\my_blog
copy .env.example .env
```

使用记事本打开并填入真实信息：
```env
# JWT 密钥 (推荐生成一个 64 位以上的随机字符串)
SECRET_KEY=your-random-secret-key-here

# 管理员密码 (用于登录后台)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password

# 生产环境 CORS 配置 (非常重要，否则后台无法调接口)
CORS_ORIGINS=https://dwill.top,https://blog.dwill.top
```

---

## 第三步：创建网络环境

由于你的 Docker 环境中有其他服务（如 postgres），我们需要确保网络连通：
```bash
# 如果 backend 网络已存在则跳过
docker network create backend
```

---

## 第四步：构建并启动

```bash
docker-compose up -d --build
```

**提示：** 首次构建需要编译前端和管理后台，大约耗时 5-10 分钟。

### 检查是否启动成功
```bash
docker ps
```
你应该能看到名为 `dwill-blog` 的容器，状态为 `Up`。

---

## 第五步：调整 Caddy 配置

在你的 `CaddyFile` 中，将之前测试用的 9990 替换为我们的博客端口 9527：

```caddy
blog.dwill.top:7777 {
    reverse_proxy localhost:9527
}
```

保存并重启/热加载 Caddy。

---

## 🔗 访问地址
- **博客前台**: [https://dwill.top](https://dwill.top)
- **管理后台**: [https://dwill.top/admin](https://dwill.top/admin)

---

## 🛠️ 常见维护操作

### 查看运行日志
```bash
docker-compose logs -f blog
```

### 数据库备份
数据库文件存放在 `data/blog.db`，直接复制保存即可。

### 更新代码
如果你在本地修改了代码想同步到服务器：
1. 覆盖服务器上的源码
2. 运行 `docker-compose up -d --build` 重新构建镜像

---

## ⚠️ 注意事项
1. **图片路径**：我已经修复了图片路径逻辑。如果你发现老文章图片还是不显示，请在后台编辑文章，确保图片路径是以 `/uploads/` 开头的相对路径。
2. **端口占用**：如果 9527 被占用，请在 `docker-compose.yml` 中修改第一个数值。
