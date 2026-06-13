with open('templates/index.html', encoding='utf-8') as f:
    text = f.read()
start = text.find('async function submitIncident')
if start != -1:
    print(text[start:start+1000].encode('ascii', 'ignore').decode())
