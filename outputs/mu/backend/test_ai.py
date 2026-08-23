import httpx, json, sys, os, struct, zlib
sys.stdout.reconfigure(encoding='utf-8')

# 构造 64x64 合法 PNG（DashScope 多模态要求图片宽高 > 10px，1x1 会被 400 拒绝）
def make_png(w=64, h=64):
    sig = b"\x89PNG\r\n\x1a\n"
    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    raw = b"".join(b"\x00" + bytes([(x * 4) % 256, (y * 4) % 256, 128]) * w for y in range(h) for x in [1])
    # 每行：过滤字节 0 + w 个 RGB 像素
    rows = b""
    for y in range(h):
        rows += b"\x00" + b"".join(bytes([(x + y) % 256, (x * 2 + y) % 256, 128]) for x in range(w))
    return sig + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")

test_png = os.path.join(os.path.dirname(__file__), 'test.png')
with open(test_png, 'wb') as f:
    f.write(make_png())

with open(test_png, 'rb') as f:
    r = httpx.post('http://localhost:8000/api/ai/analyze',
        files={'files': ('test.png', f, 'image/png')},
        data={'note': 'used for half year, fully functional'},
        timeout=150
    )
print(f"Status: {r.status_code}")
if r.status_code == 200:
    d = r.json()
    mock = d['title'].startswith('精品二手好物')
    print(f"Title: {d['title']}")
    print(f"Category: {d['category']}")
    print(f"Condition: {d['condition']}")
    print(f"Price: {d['price_min']}~{d['price_max']}")
    print(f"Tags: {d['tags']}")
    print(f"Copy: {d['copy'][:80]}...")
    print(f"Mock 降级: {'是（AI 调用失败，详见 uvicorn.log）' if mock else '否（真实 AI 结果）'}")
else:
    print(r.text[:300])

os.remove(test_png)
