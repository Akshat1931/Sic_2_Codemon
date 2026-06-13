with open('templates/index.html', encoding='utf-8') as f:
    text = f.read()
idx = text.find('function onload(')
if idx == -1:
    idx = text.find('onload =')
if idx != -1:
    print(text[idx-50:idx+400].encode('ascii', 'ignore').decode())
