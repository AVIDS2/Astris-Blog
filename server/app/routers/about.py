# 关于页面管理接口
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/about", tags=["about"])

# 关于页面 Markdown 文件路径
# 兼容 Docker 环境 (/app) 和本地开发环境
BASE_DIR = Path(__file__).parent.parent.parent  # server 目录
ABOUT_FILE = BASE_DIR.parent / "client" / "src" / "content" / "spec" / "about.md"

# Docker 环境下的备用路径
if not ABOUT_FILE.exists():
    ABOUT_FILE = Path("/app/client/src/content/spec/about.md")


class AboutContent(BaseModel):
    content: str


class AboutResponse(BaseModel):
    title: str
    content: str


def parse_markdown_frontmatter(text: str) -> tuple[str, str]:
    """解析 Markdown frontmatter，返回 (title, body)"""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            body = parts[2].strip()
            # 提取 title
            title = "关于"
            for line in frontmatter.split("\n"):
                if line.startswith("title:"):
                    title = line.replace("title:", "").strip().strip('"').strip("'")
                    break
            return title, body
    return "关于", text


def create_markdown_with_frontmatter(title: str, content: str) -> str:
    """生成带 frontmatter 的 Markdown"""
    return f'''---
title: "{title}"
---

{content}
'''


@router.get("", response_model=AboutResponse)
async def get_about_content(current_user: User = Depends(get_current_user)):
    """获取关于页面内容"""
    if not ABOUT_FILE.exists():
        raise HTTPException(status_code=404, detail="关于页面文件不存在")
    
    try:
        raw_content = ABOUT_FILE.read_text(encoding="utf-8")
        title, body = parse_markdown_frontmatter(raw_content)
        return AboutResponse(title=title, content=body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")


@router.put("")
async def update_about_content(
    data: AboutContent,
    current_user: User = Depends(get_current_user)
):
    """更新关于页面内容"""
    try:
        # 保持原有标题
        if ABOUT_FILE.exists():
            raw_content = ABOUT_FILE.read_text(encoding="utf-8")
            title, _ = parse_markdown_frontmatter(raw_content)
        else:
            title = "关于我"
        
        # 生成新文件内容
        new_content = create_markdown_with_frontmatter(title, data.content)
        
        # 写入文件
        ABOUT_FILE.write_text(new_content, encoding="utf-8")
        
        return {"message": "更新成功", "title": title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")
