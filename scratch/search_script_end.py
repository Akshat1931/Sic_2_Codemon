with open('templates/index.html', encoding='utf-8') as f:
    lines = f.readlines()
print("Total lines:", len(lines))
for idx in range(len(lines)-60, len(lines)):
    print(f'{idx+1}: {lines[idx].strip().encode("ascii", "ignore").decode()}')
