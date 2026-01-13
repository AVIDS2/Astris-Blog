"""
Bilibili 收藏夹代理 API
用于绕过浏览器跨域限制，获取公开收藏夹内容
"""
import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/bilibili", tags=["bilibili"])

BILIBILI_FAV_API = "https://api.bilibili.com/x/v3/fav/resource/list"

@router.get("/favorites/{fav_id}")
async def get_bilibili_favorites(fav_id: str, page: int = 1, page_size: int = 20):
    """
    获取 B 站公开收藏夹内容
    :param fav_id: 收藏夹 ID
    :param page: 页码
    :param page_size: 每页数量
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                BILIBILI_FAV_API,
                params={
                    "media_id": fav_id,
                    "pn": page,
                    "ps": page_size,
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://www.bilibili.com/",
                },
                timeout=10.0,
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to fetch from Bilibili")
            
            data = response.json()
            
            if data.get("code") != 0:
                raise HTTPException(status_code=400, detail=data.get("message", "Unknown error"))
            
            # 简化返回数据
            medias = data.get("data", {}).get("medias") or []
            result = []
            for item in medias:
                result.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "cover": item.get("cover"),
                    "intro": item.get("intro", ""),
                    "duration": item.get("duration", 0),
                    "link": f"https://www.bilibili.com/video/{item.get('bvid')}",
                    "upper": item.get("upper", {}).get("name", ""),
                })
            
            return {
                "items": result,
                "total": data.get("data", {}).get("info", {}).get("media_count", 0),
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to Bilibili timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
