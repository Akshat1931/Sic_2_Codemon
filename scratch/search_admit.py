with open("templates/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if "admit" in line or "evacuate" in line:
        if len(line) < 150:
            print(f"Line {i}: {line.strip()}")
