import httpx, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Test frontend
r = httpx.get('http://localhost:5173/', timeout=10)
print(f"Frontend: HTTP {r.status_code}, HTML size: {len(r.text)} bytes")

# Test API proxy
r2 = httpx.get('http://localhost:5173/api/products?page_size=2', timeout=10)
d = r2.json()
print(f"API proxy: HTTP {r2.status_code}, total: {d['total']}")

# Test detail page
r3 = httpx.get('http://localhost:5173/product/1', timeout=10)
print(f"Detail page: HTTP {r3.status_code}, HTML size: {len(r3.text)} bytes")

# Test publish page
r4 = httpx.get('http://localhost:5173/publish', timeout=10)
print(f"Publish page: HTTP {r4.status_code}, HTML size: {len(r4.text)} bytes")
