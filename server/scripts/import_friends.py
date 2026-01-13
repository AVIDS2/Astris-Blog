"""
友链数据导入脚本
运行方式: python scripts/import_friends.py
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.database import async_session, init_db
from app.models import Friend

# 友链数据
FRIENDS_DATA = [
    # ========== 原有友链 (描述改中文) ==========
    {
        "name": "Fuwari",
        "url": "https://github.com/saicaca/fuwari",
        "avatar": "https://avatars.githubusercontent.com/u/28169609?v=4",
        "description": "一个优雅的 Astro 博客模板",
        "tags": "开源,博客,Astro",
        "sort_order": 1
    },
    {
        "name": "Astro",
        "url": "https://astro.build/",
        "avatar": "https://astro.build/favicon.svg",
        "description": "现代化静态站点生成器，内容驱动开发首选",
        "tags": "框架,前端,官方",
        "sort_order": 2
    },
    
    # ========== AI 编程工具 ==========
    {
        "name": "Cursor",
        "url": "https://cursor.com/",
        "avatar": "https://cursor.com/apple-touch-icon.png",
        "description": "AI 驱动的代码编辑器，内置 GPT-4",
        "tags": "AI,编程,工具",
        "sort_order": 10
    },
    {
        "name": "Antigravity",
        "url": "https://cloud.google.com/antigravity",
        "avatar": "https://www.gstatic.com/devrel-devsite/prod/v47bd3f9f0ab21e4b5ea91606b779e8a80b37ed01c91e94a5b96c2f7e9f36b0d9/cloud/images/favicons/onecloud/favicon.ico",
        "description": "Google 出品的 AI 编程助手",
        "tags": "AI,编程,Google",
        "sort_order": 11
    },
    {
        "name": "OpenCode",
        "url": "https://github.com/opencode-ai/opencode",
        "avatar": "https://avatars.githubusercontent.com/u/157994584?s=200&v=4",
        "description": "开源 AI 编程助手，终端 IDE 体验",
        "tags": "AI,编程,开源",
        "sort_order": 12
    },
    {
        "name": "Claude",
        "url": "https://claude.ai/",
        "avatar": "https://claude.ai/favicon.ico",
        "description": "Anthropic 出品的 AI 助手，擅长编程和写作",
        "tags": "AI,对话,Anthropic",
        "sort_order": 13
    },
    {
        "name": "GitHub Copilot",
        "url": "https://github.com/features/copilot",
        "avatar": "https://github.githubassets.com/favicons/favicon.svg",
        "description": "GitHub 官方 AI 编程助手",
        "tags": "AI,编程,GitHub",
        "sort_order": 14
    },
    {
        "name": "Kiro",
        "url": "https://kiro.dev/",
        "avatar": "https://kiro.dev/favicon.ico",
        "description": "AWS 出品的 AI 代码编辑器",
        "tags": "AI,编程,AWS",
        "sort_order": 15
    },
    {
        "name": "Windsurf",
        "url": "https://codeium.com/windsurf",
        "avatar": "https://codeium.com/favicon.ico",
        "description": "Codeium 出品的 AI IDE",
        "tags": "AI,编程,IDE",
        "sort_order": 16
    },
    {
        "name": "v0.dev",
        "url": "https://v0.dev/",
        "avatar": "https://v0.dev/icon-dark-background.png",
        "description": "Vercel 出品的 AI UI 生成器",
        "tags": "AI,前端,Vercel",
        "sort_order": 17
    },
    
    # ========== AI 平台 ==========
    {
        "name": "OpenAI",
        "url": "https://openai.com/",
        "avatar": "https://openai.com/favicon.ico",
        "description": "ChatGPT 和 GPT-4 的创造者",
        "tags": "AI,GPT,官方",
        "sort_order": 20
    },
    {
        "name": "Gemini",
        "url": "https://gemini.google.com/",
        "avatar": "https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg",
        "description": "Google 最强大的多模态 AI 模型",
        "tags": "AI,Google,多模态",
        "sort_order": 21
    },
    {
        "name": "DeepSeek",
        "url": "https://www.deepseek.com/",
        "avatar": "https://www.deepseek.com/favicon.ico",
        "description": "国产高性价比 AI 大模型",
        "tags": "AI,国产,开源",
        "sort_order": 22
    },
    {
        "name": "Hugging Face",
        "url": "https://huggingface.co/",
        "avatar": "https://huggingface.co/favicon.ico",
        "description": "AI 模型社区，开源模型聚集地",
        "tags": "AI,开源,社区",
        "sort_order": 23
    },
    
    # ========== 开发框架 ==========
    {
        "name": "UniApp",
        "url": "https://uniapp.dcloud.net.cn/",
        "avatar": "https://web-assets.dcloud.net.cn/unidoc/zh/icon.png",
        "description": "跨平台应用开发框架，一套代码多端运行",
        "tags": "跨平台,框架,国产",
        "sort_order": 30
    },
    {
        "name": "Unity",
        "url": "https://unity.com/",
        "avatar": "https://unity.com/favicon.ico",
        "description": "全球领先的游戏开发引擎",
        "tags": "游戏,引擎,3D",
        "sort_order": 31
    },
    {
        "name": "React",
        "url": "https://react.dev/",
        "avatar": "https://react.dev/favicon.ico",
        "description": "Meta 出品的前端 UI 库",
        "tags": "前端,框架,Meta",
        "sort_order": 32
    },
    {
        "name": "Vue.js",
        "url": "https://vuejs.org/",
        "avatar": "https://vuejs.org/logo.svg",
        "description": "渐进式 JavaScript 框架",
        "tags": "前端,框架,开源",
        "sort_order": 33
    },
    {
        "name": "Next.js",
        "url": "https://nextjs.org/",
        "avatar": "https://nextjs.org/favicon.ico",
        "description": "React 全栈框架，Vercel 出品",
        "tags": "前端,框架,Vercel",
        "sort_order": 34
    },
    {
        "name": "Svelte",
        "url": "https://svelte.dev/",
        "avatar": "https://svelte.dev/favicon.png",
        "description": "编译时前端框架，无虚拟 DOM",
        "tags": "前端,框架,创新",
        "sort_order": 35
    },
    {
        "name": "FastAPI",
        "url": "https://fastapi.tiangolo.com/",
        "avatar": "https://fastapi.tiangolo.com/img/favicon.png",
        "description": "现代高性能 Python Web 框架",
        "tags": "后端,Python,API",
        "sort_order": 36
    },
    
    # ========== 云服务 ==========
    {
        "name": "Cloudflare",
        "url": "https://www.cloudflare.com/",
        "avatar": "https://www.cloudflare.com/favicon.ico",
        "description": "全球 CDN 和边缘计算平台",
        "tags": "云服务,CDN,安全",
        "sort_order": 40
    },
    {
        "name": "Vercel",
        "url": "https://vercel.com/",
        "avatar": "https://vercel.com/favicon.ico",
        "description": "前端部署平台，秒级部署体验",
        "tags": "云服务,部署,Serverless",
        "sort_order": 41
    },
    {
        "name": "Supabase",
        "url": "https://supabase.com/",
        "avatar": "https://supabase.com/favicon/favicon.ico",
        "description": "开源 Firebase 替代方案",
        "tags": "云服务,数据库,开源",
        "sort_order": 42
    },
    {
        "name": "Railway",
        "url": "https://railway.app/",
        "avatar": "https://railway.app/favicon.ico",
        "description": "现代化应用部署平台",
        "tags": "云服务,部署,PaaS",
        "sort_order": 43
    },
    
    # ========== 开发工具 ==========
    {
        "name": "VS Code",
        "url": "https://code.visualstudio.com/",
        "avatar": "https://code.visualstudio.com/favicon.ico",
        "description": "微软出品的代码编辑器",
        "tags": "工具,编辑器,微软",
        "sort_order": 50
    },
    {
        "name": "Docker",
        "url": "https://www.docker.com/",
        "avatar": "https://www.docker.com/wp-content/uploads/2023/04/cropped-Docker-favicon-192x192.png",
        "description": "容器化技术领导者",
        "tags": "工具,容器,DevOps",
        "sort_order": 51
    },
    {
        "name": "Figma",
        "url": "https://www.figma.com/",
        "avatar": "https://static.figma.com/app/icon/1/favicon.png",
        "description": "协作式 UI 设计工具",
        "tags": "设计,工具,协作",
        "sort_order": 52
    },
    {
        "name": "Notion",
        "url": "https://www.notion.so/",
        "avatar": "https://www.notion.so/images/favicon.ico",
        "description": "All-in-One 知识管理工具",
        "tags": "工具,笔记,协作",
        "sort_order": 53
    },
    
    # ========== 技术社区 ==========
    {
        "name": "GitHub",
        "url": "https://github.com/",
        "avatar": "https://github.githubassets.com/favicons/favicon.svg",
        "description": "全球最大的代码托管平台",
        "tags": "社区,开源,代码",
        "sort_order": 60
    },
    {
        "name": "Stack Overflow",
        "url": "https://stackoverflow.com/",
        "avatar": "https://cdn.sstatic.net/Sites/stackoverflow/Img/favicon.ico",
        "description": "程序员问答社区",
        "tags": "社区,问答,学习",
        "sort_order": 61
    },
    {
        "name": "掘金",
        "url": "https://juejin.cn/",
        "avatar": "https://lf-web-assets.juejin.cn/obj/juejin-web/xitu_juejin_web/static/favicons/favicon-32x32.png",
        "description": "中文技术社区",
        "tags": "社区,博客,国产",
        "sort_order": 62
    },
    {
        "name": "V2EX",
        "url": "https://www.v2ex.com/",
        "avatar": "https://www.v2ex.com/static/img/icon_rayps_64.png",
        "description": "创意工作者社区",
        "tags": "社区,讨论,创意",
        "sort_order": 63
    },
    
    # ========== 学习资源 ==========
    {
        "name": "MDN Web Docs",
        "url": "https://developer.mozilla.org/",
        "avatar": "https://developer.mozilla.org/favicon-48x48.png",
        "description": "Web 开发权威文档",
        "tags": "学习,文档,官方",
        "sort_order": 70
    },
    {
        "name": "菜鸟教程",
        "url": "https://www.runoob.com/",
        "avatar": "https://www.runoob.com/favicon.ico",
        "description": "编程入门学习网站",
        "tags": "学习,教程,入门",
        "sort_order": 71
    },
    {
        "name": "LeetCode",
        "url": "https://leetcode.cn/",
        "avatar": "https://leetcode.cn/favicon.ico",
        "description": "算法刷题平台",
        "tags": "学习,算法,面试",
        "sort_order": 72
    },
]


async def import_friends():
    """导入友链数据"""
    await init_db()
    
    async with async_session() as db:
        # 检查是否已有数据
        from sqlalchemy import select, func
        result = await db.execute(select(func.count()).select_from(Friend))
        count = result.scalar()
        
        if count > 0:
            print(f"⚠️ 数据库已存在 {count} 条友链数据")
            confirm = input("是否清空并重新导入？(y/N): ")
            if confirm.lower() != 'y':
                print("取消导入")
                return
            
            # 清空现有数据
            from sqlalchemy import delete
            await db.execute(delete(Friend))
            await db.commit()
            print("✅ 已清空现有数据")
        
        # 导入数据
        for friend_data in FRIENDS_DATA:
            friend = Friend(
                name=friend_data["name"],
                url=friend_data["url"],
                avatar=friend_data.get("avatar", ""),
                description=friend_data.get("description", ""),
                tags=friend_data.get("tags", ""),
                sort_order=friend_data.get("sort_order", 0),
                is_visible=True
            )
            db.add(friend)
        
        await db.commit()
        print(f"✅ 成功导入 {len(FRIENDS_DATA)} 条友链数据！")


if __name__ == "__main__":
    asyncio.run(import_friends())
