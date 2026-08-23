import httpx, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000/api"

# 1. 测试注册（密码需满足强度：>=8位，字母+数字）
r = httpx.post(f"{BASE}/auth/register", json={"username": "testuser", "password": "test12345", "phone": "13900139000"})
print(f"Register: {r.status_code} - {r.json().get('user', {}).get('username') or r.json().get('detail')}")

# 2. 测试登录
r = httpx.post(f"{BASE}/auth/login", json={"username": "testuser", "password": "test12345", "phone": "13900139000"})
token = r.json()["access_token"]
test_uid = r.json()["user"]["id"]
print(f"Login: {r.status_code} - token={token[:30]}...")

# 3. 测试获取当前用户
r = httpx.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {token}"})
print(f"Me: {r.status_code} - {r.json()['username']}")

# 4. 测试管理员登录（新默认口令，见 .env 的 ADMIN_DEFAULT_PASSWORD）
r = httpx.post(f"{BASE}/auth/login", json={"username": "admin", "password": "admin@12345"})
admin_token = r.json()["access_token"]
print(f"Admin login: {r.status_code} - role={r.json()['user']['role']}")

# 5. 测试发布商品（需登录）
r = httpx.post(f"{BASE}/products", json={
    "title": "测试商品",
    "category": "数码",
    "condition": "9成新",
    "ai_price_min": 100,
    "ai_price_max": 200,
    "ai_tags": ["测试"],
    "ai_copy": "测试文案",
    "contact": "微信: test",
    "images": [],
    "user_note": "测试"
}, headers={"Authorization": f"Bearer {token}"})
print(f"Create product: {r.status_code} - id={r.json().get('id')}")

# 6. 测试我的商品
r = httpx.get(f"{BASE}/my/products", headers={"Authorization": f"Bearer {token}"})
print(f"My products: {r.status_code} - total={r.json()['total']}")

# 7. 测试管理员查看所有商品
r = httpx.get(f"{BASE}/admin/all", headers={"Authorization": f"Bearer {admin_token}"})
print(f"Admin all: {r.status_code} - total={r.json()['total']}")

# 8. 敏感词测试（拦截模式：直接返回 400，不再标记后审）
r = httpx.post(f"{BASE}/products", json={
    "title": "卖毒品冰毒",
    "category": "其他",
    "condition": "全新",
    "ai_price_min": 1,
    "ai_price_max": 2,
    "ai_tags": [],
    "ai_copy": "违禁品",
    "contact": "test",
    "images": [],
    "user_note": ""
}, headers={"Authorization": f"Bearer {token}"})
detail = r.json().get("detail", "")
status = "PASS" if r.status_code == 400 and "拦截" in detail else "FAIL"
print(f"[{status}] Sensitive-word block: {r.status_code} - {detail[:60]}")

# 9. 管理员查看被标记商品（管理员手动下架仍会标记，接口保留）
r = httpx.get(f"{BASE}/admin/flagged", headers={"Authorization": f"Bearer {admin_token}"})
print(f"Flagged list: {r.status_code} - total={r.json()['total']}")

# 10. 清理：删除本测试账号（连带其名下商品与图片）
r = httpx.delete(f"{BASE}/admin/users/{test_uid}", headers={"Authorization": f"Bearer {admin_token}"})
print(f"Cleanup test account: {r.status_code} - {r.json().get('message', '')}")

print("\n=== 全部测试通过 ===")
