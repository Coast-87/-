import httpx, json, sys
sys.stdout.reconfigure(encoding='utf-8')

r = httpx.get('http://localhost:8000/api/products?page=1&page_size=10')
d = r.json()
print(f"Total: {d['total']}")
for p in d['items']:
    print(f"  [{p['category']}] {p['title']} - {p['status']}")

# Test filters
r2 = httpx.get('http://localhost:8000/api/products?status=sold')
print(f"Sold: {r2.json()['total']}")

r3 = httpx.get('http://localhost:8000/api/products?keyword=MacBook')
print(f"Search MacBook: {r3.json()['total']}")
