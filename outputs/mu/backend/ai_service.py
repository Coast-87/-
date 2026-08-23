"""多模态 AI 服务——调用大模型进行图片识别、成色分析、估价与文案生成"""
import os
import base64
import json
import logging
import httpx
from typing import List

logger = logging.getLogger("flea-market")

# 配置：支持 OpenAI 兼容的多模态 API
API_KEY = os.getenv("OPENAI_API_KEY", "sk-your-api-key-here")
API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("AI_MODEL", "gpt-4o")
# 联网搜索开关：估价时参考实时二手行情（仅部分服务商支持，如阿里云百炼；换用不支持的服务商时设为 false）
ENABLE_SEARCH = os.getenv("AI_ENABLE_SEARCH", "true").strip().lower() in ("1", "true", "yes", "on")

SYSTEM_PROMPT = """你是一个校园二手物品交易平台的智能发品助手。用户会上传1-3张二手物品照片，并可能附带简短说明。

请根据图片和用户说明，生成以下JSON格式的分析结果（只返回JSON，不要其他内容）：
{
  "title": "简洁吸引人的商品标题（15字以内）",
  "category": "分类：数码/书籍/生活用品/服饰/美妆/运动户外/其他",
  "condition": "成色等级：全新/99新/95新/9成新/8成新/7成新/有瑕疵",
  "price_min": 推荐最低价格（数字），
  "price_max": 推荐最高价格（数字），
  "tags": ["标签1", "标签2", "标签3"],
  "copy_text": "一段适合校园跳蚤群传播的带货文案，口语化、有感染力，80-150字，包含emoji"
}

注意：
- 根据物品原价和成色合理估价，校园二手通常为原价3-7折；如可获取联网信息，请优先参考当前二手市场实际行情
- 若用户补充说明中提供了品牌/型号、购入价格、购入时间，请优先以此识别商品，并以购入价格作为原价基准，结合成色与保值率估价
- 标签要突出卖点，如"高性价比"、"九成新"、"正品"等
- 文案要活泼有趣，适合大学生群体
"""

async def analyze_product_images(image_paths: List[str], user_note: str = "") -> dict:
    """调用多模态大模型分析商品图片"""
    
    # 构建多模态消息内容
    content = []
    
    # 添加图片
    for img_path in image_paths:
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")
            
            # 判断图片格式
            ext = os.path.splitext(img_path)[1].lower()
            mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif"}
            mime_type = mime_map.get(ext, "image/jpeg")
            
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{img_base64}",
                    "detail": "auto"
                }
            })
    
    # 添加文本说明
    text_prompt = SYSTEM_PROMPT
    if user_note:
        text_prompt += f"\n\n用户补充说明：{user_note}"
    
    content.append({"type": "text", "text": text_prompt})
    
    # 调用 API
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "user", "content": content}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.7,
                    "response_format": {"type": "json_object"},
                    **({"enable_search": True} if ENABLE_SEARCH else {})
                }
            )
            response.raise_for_status()
            data = response.json()
            
            result_text = data["choices"][0]["message"]["content"]
            # 清理可能的 markdown 代码块
            result_text = result_text.strip()
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            result_text = result_text.strip()
            
            data = json.loads(result_text)
            # 模型输出可能缺字段/类型不稳定：兜底补齐，避免下游 schema 校验 500
            _defaults = {"title": "", "category": "生活用品", "condition": "9成新", "price_min": 0, "price_max": 0}
            for _k, _v in _defaults.items():
                if data.get(_k) is None:
                    data[_k] = _v
            if not isinstance(data.get("tags"), list):
                data["tags"] = []
            if "copy_text" not in data and "copy" not in data:
                data["copy_text"] = ""
            return data
            
        except Exception as e:
            # 记录完整错误后降级为模拟数据（仅开发兜底，真实环境应能看到具体失败原因）
            logger.error(f"AI API 调用失败，降级为模拟数据: {e}", exc_info=True)
            return _mock_analysis(user_note)

def _mock_analysis(user_note: str = "") -> dict:
    """当 AI API 不可用时的模拟分析"""
    return {
        "title": "精品二手好物｜学生党必备" + ("｜" + user_note[:8] if user_note else ""),
        "category": "生活用品",
        "condition": "9成新",
        "price_min": 30,
        "price_max": 80,
        "tags": ["高性价比", "九成新", "学生党必备"],
        "copy_text": f"🎉 捡漏时间到！这件宝贝成色超新，功能完好，价格美丽！💯 学生党预算有限也能拥有好物～闲置不如变现，手慢无哦！🔥 感兴趣的小伙伴速来滴滴我，支持学校面交自提！📦"
    }
