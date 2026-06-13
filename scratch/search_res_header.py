with open('templates/index.html', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if 'id="section-resources"' in l:
        for idx in range(i, i+30):
            print(f'{idx+1}: {lines[idx].strip().encode("ascii", "ignore").decode()}')
        break
