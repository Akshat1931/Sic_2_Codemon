with open('templates/index.html', encoding='utf-8') as f:
    lines = f.readlines()
for idx in range(1281, 1289):
    print(f'{idx+1}: {repr(lines[idx])}')
