with open('templates/index.html', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if 'doallocate' in l.lower() or 'id="alloc' in l.lower() or 'id=\'alloc' in l.lower() or 'id="nav-resources"' in l.lower():
        print(f'{i+1}: {l.strip()[:100]}')
