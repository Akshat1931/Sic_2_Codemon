with open('templates/index.html', encoding='utf-8') as f:
    text = f.read()
start = text.find('async function apiFetch')
if start != -1:
    end = text.find('}', start)
    print(text[start:end+1])
else:
    print('apiFetch not found')
