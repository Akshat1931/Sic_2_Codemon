with open("templates/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

keywords = ["planRoute", "/api/route", "routes", "alternative-routes", "route-result"]

for i, line in enumerate(lines, 1):
    for kw in keywords:
        if kw in line:
            print(f"Line {i}: {line.strip()}")
            break
