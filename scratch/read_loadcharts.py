with open('templates/index.html', encoding='utf-8') as f:
    text = f.read()
start = text.find('async function loadCharts()')
if start != -1:
    end = text.find('// ', start + 30)
    print(text[start:end].encode('ascii', 'ignore').decode())
