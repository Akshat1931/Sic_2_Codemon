with open('templates/index.html', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if 'async function loadCharts()' in l:
        print(f"Starts at line: {i+1}")
        # search for end of function (close bracket at start of line)
        for idx in range(i+1, len(lines)):
            if lines[idx].strip() == '}':
                print(f"Ends at line: {idx+1}")
                break
        break
