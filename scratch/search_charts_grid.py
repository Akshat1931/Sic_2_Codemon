with open('templates/index.html', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if 'id="charts-grid"' in l:
        for idx in range(i-2, i+10):
            print(f'{idx+1}: {lines[idx].strip().encode("ascii", "ignore").decode()}')
        break
