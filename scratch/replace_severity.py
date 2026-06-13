import re

with open('templates/index.html', encoding='utf-8') as f:
    content = f.read()

# Locate the inc-severity block using regex to ignore the strange character
pattern = r'<div class="form-group">\s*<label class="form-label">Severity Level</label>\s*<select class="form-control" id="inc-severity" required>\s*<option value="">Severity[^<]*</option>\s*<option>Low</option><option>Medium</option>\s*<option>High</option><option>Critical</option>\s*</select>\s*</div>'

replacement = """<div class="form-group">
                  <label class="form-label">Severity Level <span style="font-size:0.65rem;color:var(--text-muted)">*(Auto)*</span></label>
                  <select class="form-control" id="inc-severity" disabled style="opacity: 0.85; cursor: not-allowed; background: rgba(0,0,0,0.15)" required>
                    <option value="">Severity</option>
                    <option>Low</option><option>Medium</option>
                    <option>High</option><option>Critical</option>
                  </select>
                </div>"""

new_content = re.sub(pattern, replacement, content)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replacement complete!")
