import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

keywords = ["inc-severity", "inc-population", "submitIncident", "loadCharts", "chart", "Canvas", "chartInstances"]

for i, line in enumerate(lines, 1):
    for kw in keywords:
        if kw in line:
            print(f"Line {i}: {line.strip()}")
            break
