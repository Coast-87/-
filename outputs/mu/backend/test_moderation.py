"""拦截机制测试：文本敏感词拦截 + 违规图片拦截"""
import httpx, sys, io, time, struct, zlib
sys.stdout.reconfigure(encoding='utf-8')
BASE = "http://localhost:8000/api"

client = httpx.Client(base_url=BASE, timeout=30)
results = []

def check(name, cond, extra=""):
    results.append(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {extra}")

def make_png() -> bytes:
    """构造 1x1 最小合法 PNG"""
    sig = b"\x89PNG\r\n\x1a\n"
    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff"))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + iend

# ==================== 准备测试账号 ====================
uname = f"modtest{int(time.time()) % 1000000}"
r = client.post("/auth/register", json={"username": uname, "password": "abc12345", "phone": "13800138000"})
if r.status_code != 200:
    r = client.post("/auth/login", json={"username": uname, "password": "abc12345"})
token = r.json()["access_token"]
uid = r.json().get("user", {}).get("id")
headers = {"Authorization": f"Bearer {token}"}
check("测试账号就绪", bool(token), uname)

# ==================== 1. 文本预检接口 ====================
r = client.post("/moderation/check", json={"text": "九成新高等数学课本出售"}, headers=headers)
check("预检-正常文本放行", r.status_code == 200 and r.json().get("flagged") is False)

r = client.post("/moderation/check", json={"text": "出售大麻和冰毒"}, headers=headers)
body = r.json()
check("预检-敏感文本识别", r.status_code == 200 and body.get("flagged") is True, str(body.get("words", [])))

# 变体绕过拦截（加空格/符号/谐音）
r = client.post("/moderation/check", json={"text": "傻 逼"}, headers=headers)
check("预检-空格变体拦截", r.status_code == 200 and r.json().get("flagged") is True)
r = client.post("/moderation/check", json={"text": "刷-单 兼职"}, headers=headers)
check("预检-符号变体拦截", r.status_code == 200 and r.json().get("flagged") is True)
r = client.post("/moderation/check", json={"text": "沙比"}, headers=headers)
check("预检-谐音变体拦截", r.status_code == 200 and r.json().get("flagged") is True)
r = client.post("/moderation/check", json={"text": "出钓鱼竿一支"}, headers=headers)
check("预检-正常商品词放行", r.status_code == 200 and r.json().get("flagged") is False)

# ==================== 2. 发布商品敏感词拦截 ====================
r = client.post("/products", json={
    "title": "出售枪支弹药", "category": "其他", "condition": "9成新",
}, headers=headers)
check("发布-标题敏感词拦截", r.status_code == 400 and "拦截" in r.json().get("detail", ""), r.json().get("detail", "")[:60])

r = client.post("/products", json={
    "title": "正常笔记本", "category": "数码", "condition": "9成新",
    "user_note": "加微信参与刷单兼职",
}, headers=headers)
check("发布-补充说明敏感词拦截", r.status_code == 400, r.json().get("detail", "")[:60])

r = client.post("/products", json={
    "title": "正常笔记本", "category": "数码", "condition": "9成新",
    "contact": "约炮联系我",
}, headers=headers)
check("发布-联系方式敏感词拦截", r.status_code == 400, r.json().get("detail", "")[:60])

r = client.post("/products", json={
    "title": "正常笔记本", "category": "数码", "condition": "9成新",
    "ai_tags": ["高性价比", "赌博神器"],
}, headers=headers)
check("发布-标签敏感词拦截", r.status_code == 400, r.json().get("detail", "")[:60])

# ==================== 3. 正常内容放行 ====================
r = client.post("/products", json={
    "title": "九成新高等数学课本", "category": "书籍", "condition": "9成新",
    "ai_price_min": 10, "ai_price_max": 20, "contact": "wx: test123",
}, headers=headers)
check("发布-正常内容放行", r.status_code == 200)
pid = r.json().get("id")

# 误伤回归：商品语境正常词不得拦截
for title in ["出钓鱼竿一支，带浮漂和鱼线", "高数教材带答案解析",
              "毕业证封皮外壳红色烫金", "小姐姐风连衣裙", "儿童小木马玩具"]:
    r = client.post("/products", json={
        "title": title, "category": "其他", "condition": "9成新",
    }, headers=headers)
    check(f"发布-误伤回归放行[{title[:12]}]", r.status_code == 200, r.json().get("detail", "")[:40])

# 变体绕过：发布时应拦截
r = client.post("/products", json={"title": "约 炮", "category": "其他", "condition": "9成新"}, headers=headers)
check("发布-空格变体拦截", r.status_code == 400)
r = client.post("/products", json={"title": "出 售 枪 支", "category": "其他", "condition": "9成新"}, headers=headers)
check("发布-符号变体拦截", r.status_code == 400)

# ==================== 4. 更新商品敏感词拦截 ====================
if pid:
    r = client.put(f"/products/{pid}", json={"title": "赌博网站推广"}, headers=headers)
    check("更新-敏感词拦截", r.status_code == 400, r.json().get("detail", "")[:60])

# ==================== 5. 违规图片拦截 ====================
# 5.1 伪装图片（文本内容伪装 .jpg）
files = {"file": ("fake.jpg", io.BytesIO(b"this is not an image at all"), "image/jpeg")}
r = client.post("/upload", files=files, headers=headers)
check("上传-伪装图片拦截", r.status_code == 400, r.json().get("detail", "")[:60])

# 5.2 扩展名与实际内容不符（PNG 内容伪装 .jpg）
png = make_png()
files = {"file": ("mismatch.jpg", io.BytesIO(png), "image/jpeg")}
r = client.post("/upload", files=files, headers=headers)
check("上传-格式不符拦截", r.status_code == 400, r.json().get("detail", "")[:60])

# 5.3 不支持的扩展名
files = {"file": ("evil.exe", io.BytesIO(b"MZ\x90\x00"), "application/octet-stream")}
r = client.post("/upload", files=files, headers=headers)
check("上传-非法扩展名拦截", r.status_code == 400)

# 5.4 正常图片放行（AI 审核不可用时降级为仅本地校验，应通过）
files = {"file": ("real.png", io.BytesIO(png), "image/png")}
r = client.post("/upload", files=files, headers=headers)
check("上传-正常图片放行", r.status_code == 200, r.json().get("url", ""))

# 5.5 AI 分析接口 - 伪装图片拦截
files = {"files": ("fake.jpg", io.BytesIO(b"not image content"), "image/jpeg")}
r = client.post("/ai/analyze", files=files, headers=headers)
check("AI分析-伪装图片拦截", r.status_code == 400, r.json().get("detail", "")[:60])

# ==================== 清理 ====================
if pid:
    client.delete(f"/products/{pid}", headers=headers)
# 删除测试账号（连带其名下商品/图片）
_r = client.post("/auth/login", json={"username": "admin", "password": "admin@12345"})
if _r.status_code == 200 and uid:
    client.delete(f"/admin/users/{uid}", headers={"Authorization": f"Bearer {_r.json()['access_token']}"})

passed, total = sum(results), len(results)
print(f"\n结果: {passed}/{total} 通过")
sys.exit(0 if passed == total else 1)
