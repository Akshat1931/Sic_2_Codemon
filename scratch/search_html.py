import re

with open('templates/index.html', encoding='utf-8') as f:
    text = f.read()

print("=== IDS ===")
ids = re.findall(r'id=["\']([a-zA-Z0-9_\-]+)["\']', text)
for i in sorted(list(set(ids))):
    print(" ", i)

print("\n=== JS FUNCTIONS ===")
funcs = re.findall(r'function\s+(\w+)\s*\(', text)
funcs += re.findall(r'(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', text)
for f in sorted(list(set(funcs))):
    print(" ", f)
