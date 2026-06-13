with open('templates/index.html', encoding='utf-8') as f:
    text = f.read()
start = text.find('window.onload')
if start != -1:
    print(text[start:start+400].encode('ascii', 'ignore').decode())
else:
    # search for onload function
    start = text.find('onload()')
    if start != -1:
         print(text[start:start+400].encode('ascii', 'ignore').decode())
