"""违规图片审核模块：本地魔数校验 + AI 多模态内容审核"""
import os
import base64
import json
import logging
import httpx

logger = logging.getLogger("flea-market")

API_KEY = os.getenv("OPENAI_API_KEY", "sk-your-api-key-here")
API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("AI_MODEL", "gpt-4o")

# 审核模式: ai=AI审核+本地校验（默认）/ local=仅本地校验 / off=关闭审核
MODERATION_MODE = os.getenv("IMAGE_MODERATION", "ai").strip().lower()

_MIME_MAP = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".webp": "image/webp", ".gif": "image/gif",
}

_MODERATION_PROMPT = """你是校园二手交易平台的图片内容审核员。请审核这张图片是否包含以下违规内容：
1. 色情低俗：裸体、色情、性暗示内容
2. 暴力血腥：暴力、血腥、虐待、自残内容
3. 违禁物品：枪支、弹药、管制刀具、毒品、假币等违禁品
4. 敏感内容：政治敏感、邪教、恐怖主义相关内容
5. 诈骗信息：可疑二维码、诈骗广告、钓鱼链接截图
6. 个人隐私：他人身份证、银行卡、学生证等隐私证件照片

审核原则：
- 这是校园二手交易平台，手机、电脑、键盘、鼠标等数码产品及外设、书籍、衣物、生活用品都是正常商品，不得判定违规
- 疑罪从无：仅当明确、确信图片包含上述违规内容时才 flagged=true；模糊、不确定一律 flagged=false
- flagged=true 时必须在 reason 中写明具体违规类型及图片中的具体内容，reason 不得为空；若无法给出具体理由，说明证据不足，应视为不违规

仅返回JSON，格式：{"flagged": true/false, "reason": "违规类型及简短说明"}
若图片正常，reason 为空字符串。"""

def verify_image_header(filepath: str, ext: str) -> str:
    """校验文件头魔数与扩展名一致，防止伪装成图片的非图片文件。
    返回真实图片格式；校验失败抛出 ValueError。"""
    with open(filepath, "rb") as f:
        head = f.read(16)
    if not head:
        raise ValueError("文件内容为空")

    if head.startswith(b"\xff\xd8\xff"):
        fmt = "jpeg"
    elif head.startswith(b"\x89PNG\r\n\x1a\n"):
        fmt = "png"
    elif head.startswith((b"GIF87a", b"GIF89a")):
        fmt = "gif"
    elif head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        fmt = "webp"
    else:
        raise ValueError("文件内容不是有效的图片")

    expected = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}
    if expected.get(ext.lstrip("."), "") != fmt:
        raise ValueError(f"文件实际内容（{fmt}）与扩展名 {ext} 不符")
    return fmt

async def moderate_image(filepath: str) -> tuple[bool, str]:
    """审核图片是否违规，返回 (是否违规, 违规原因)。
    - 本地魔数校验始终执行（不合法直接抛 ValueError）
    - AI 审核失败时降级为仅本地校验放行，并记录日志
    """
    ext = os.path.splitext(filepath)[1].lower()
    verify_image_header(filepath, ext)

    if MODERATION_MODE in ("off", "local"):
        return False, ""

    try:
        with open(filepath, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        mime = _MIME_MAP.get(ext, "image/jpeg")

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL_NAME,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}", "detail": "low"}},
                            {"type": "text", "text": _MODERATION_PROMPT},
                        ],
                    }],
                    "max_tokens": 200,
                    "temperature": 0,
                    "response_format": {"type": "json_object"}
                }
            )
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"].strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)

            flagged = bool(data.get("flagged"))
            reason = str(data.get("reason") or "").strip()
            # 模型判定违规但未给出具体原因：视为证据不足，放行并记录日志，
            # 避免正常商品（如键盘等数码外设）被无理由误拦截
            if flagged and not reason:
                logger.warning(f"Image moderation flagged without reason, treated as pass: {os.path.basename(filepath)}")
                return False, ""
            if flagged:
                logger.warning(f"Image moderation flagged: {os.path.basename(filepath)}, reason={reason}")
            return flagged, reason

    except Exception as e:
        # AI 审核不可用时降级为仅本地校验，不阻断正常发布
        logger.error(f"Image moderation unavailable, degraded to local-only check: {e}")
        return False, ""
