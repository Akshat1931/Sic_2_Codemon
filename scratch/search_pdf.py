with open("scratch/pdf_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

import re
keywords = ["allocate", "allocation", "resource", "greedy", "knapsack", "weight", "capacity", "limit"]
lines = text.split("\n")
for i, line in enumerate(lines, 1):
    for kw in keywords:
        if kw in line.lower():
            print(f"Line {i}: {line.strip()}")
            break
