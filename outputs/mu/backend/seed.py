import httpx, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000/api"

# 登录 admin
r = httpx.post(f"{BASE}/auth/login", json={"username": "admin", "password": "admin123"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

products = [
    {"title":"Apple MacBook Air M3 2024款","category":"数码","condition":"95新","ai_price_min":5800,"ai_price_max":6800,"ai_tags":["95新","高性价比","在保"],"ai_copy":"学姐毕业出MacBook Air M3！用了不到一年，成色超新，电池健康度98%！轻办公、追剧、写论文完全不卡。毕业急出，价格好商量～","contact":"微信：senior_sis2024","images":[],"user_note":"入手半年"},
    {"title":"高等数学（第七版）上下册 全新","category":"书籍","condition":"全新","ai_price_min":25,"ai_price_max":40,"ai_tags":["全新","考研必备","白菜价"],"ai_copy":"全新高数上下册！买来就没翻开过...考研党、期末复习的学弟学妹必入！比书店便宜一半～","contact":"QQ：1234567890","images":[],"user_note":"全新未拆封"},
    {"title":"小米台灯1S 护眼LED 极简设计","category":"生活用品","condition":"9成新","ai_price_min":35,"ai_price_max":60,"ai_tags":["9成新","护眼","颜值高"],"ai_copy":"小米台灯1S，颜值超高！无频闪不伤眼，熬夜写论文必备！宿舍桌面C位神器，毕业了带不走便宜出～","contact":"微信：xiaomi_fan","images":[],"user_note":"功能正常"},
    {"title":"Nike Air Force 1 纯白 42码","category":"运动户外","condition":"8成新","ai_price_min":200,"ai_price_max":350,"ai_tags":["经典款","百搭","8成新"],"ai_copy":"经典AF1纯白42码！穿了一个学期正常磨损，清洁一下跟新的一样！百搭神鞋，毕业清仓诚心要可小刀～","contact":"微信：sneakerhead","images":[],"user_note":"正常磨损"},
    {"title":"完美日记小猫盘眼影 仅试色","category":"美妆","condition":"99新","ai_price_min":30,"ai_price_max":50,"ai_tags":["99新","仅试色","正品"],"ai_copy":"完美日记小猫盘！仅试色一次基本全新！颜色超温柔日常妆通勤妆都合适，粉质细腻好晕染～便宜出给喜欢化妆的姐妹！","contact":"微信：makeup_lover","images":[],"user_note":"仅试色"},
]

for p in products:
    r = httpx.post(f"{BASE}/products", json=p, headers=headers)
    print(f"Created: {p['title'][:20]}... id={r.json()['id']}")

print(f"\nDone! {len(products)} seed products created.")
