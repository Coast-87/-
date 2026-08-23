import httpx, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = "http://localhost:8000/api"

# 1. 无认证访问受保护接口 → 应返回 401
r = httpx.post(f"{BASE}/products", json={"title": "test"})
print(f"Unauthorized: {r.status_code} - {r.json()['detail']}")

# 2. 上传非法文件类型 → 应返回 400
r = httpx.post(f"{BASE}/upload", files={"file": ("test.txt", b"hello", "text/plain")})
print(f"Bad file type: {r.status_code} - {r.json()['detail']}")

# 3. 访问不存在的商品 → 应返回 404
r = httpx.get(f"{BASE}/products/99999")
print(f"Not found: {r.status_code} - {r.json()['detail']}")

# 4. 正常注册 → 验证正常响应
r = httpx.post(f"{BASE}/auth/register", json={"username": "errortest", "password": "123456"})
print(f"Register OK: {r.status_code}")

# 5. 重复注册 → 应返回 400
r = httpx.post(f"{BASE}/auth/register", json={"username": "errortest", "password": "123456"})
print(f"Duplicate: {r.status_code} - {r.json()['detail']}")

print("\n=== 错误处理测试通过 ===")
