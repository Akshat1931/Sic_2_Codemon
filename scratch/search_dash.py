with open('templates/index.html', encoding='utf-8') as f:
    text = f.read()
idx = text.find('id="section-dashboard"')
if idx != -1:
    print(text[idx-200:idx+600].encode('ascii', 'ignore').decode())
