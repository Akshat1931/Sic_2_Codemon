with open("templates/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if "RESOURCE ALLOCATION HISTORY LOG" in line or "alloc-log-count" in line:
        print(f"Line {i}: {line.strip()}")
