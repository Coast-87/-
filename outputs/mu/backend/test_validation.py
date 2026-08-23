"""注册字段校验测试（与 schemas.UserRegister 当前行为对齐）"""
import urllib.request, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')
BASE = "http://localhost:8000/api"

PHONE = "13800138000"
SUFFIX = str(time.time_ns())[-8:]  # 保证可重复运行

# (用户名, 密码, 期望出现在错误信息中的关键字；None 表示期望注册成功)
# 注意：密码长度不足时由 pydantic min_length 先返回英文内置信息
tests = [
    ("test@user", "12345678a", "中文、英文、数字"),
    ("用户 名", "12345678a", "中文、英文、数字"),
    ("valuser" + SUFFIX, "12345", "at least 8 characters"),
    ("valuser" + SUFFIX, "12345678", "字母+数字"),
    ("valuser" + SUFFIX, "abcdefg1", None),
    ("valuser" + SUFFIX, "abcdefg1", "已存在"),
]

fails = 0
for username, password, expected in tests:
    data = json.dumps({"username": username, "password": password, "phone": PHONE}).encode()
    req = urllib.request.Request(f"{BASE}/auth/register", data=data,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read())
            detail = str(body.get("detail", ""))
            ok = expected is None
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        detail = body.get("detail", "")
        if isinstance(detail, list):
            detail = " | ".join(d.get("msg", "") for d in detail)
        detail = str(detail)
        ok = expected is not None and expected in detail
    except Exception as e:
        detail = f"ERR: {e}"
        ok = False
    if not ok:
        fails += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {username}:{password} => {detail[:80]}")

# 清理：删除本轮成功注册的 valuser 账号，避免残留
try:
    _data = json.dumps({"username": "admin", "password": "admin@12345"}).encode()
    _req = urllib.request.Request(f"{BASE}/auth/login", data=_data,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(_req, timeout=5) as _resp:
        _admin = json.loads(_resp.read())["access_token"]
    _req = urllib.request.Request(f"{BASE}/admin/users?page_size=100",
        headers={"Authorization": f"Bearer {_admin}"})
    with urllib.request.urlopen(_req, timeout=5) as _resp:
        _items = json.loads(_resp.read())["items"]
    for _u in _items:
        if _u["username"] == "valuser" + SUFFIX:
            _req = urllib.request.Request(f"{BASE}/admin/users/{_u['id']}",
                headers={"Authorization": f"Bearer {_admin}"}, method="DELETE")
            with urllib.request.urlopen(_req, timeout=5) as _resp:
                print("已清理测试账号:", json.loads(_resp.read()).get("message", ""))
except Exception as _e:
    print("清理测试账号失败（不影响测试结果）:", _e)

print(f"\n{'全部通过' if fails == 0 else f'{fails} 项失败'}")
sys.exit(1 if fails else 0)
