with open('templates/index.html', encoding='utf-8') as f:
    text = f.read()
idx = text.find('id="section-routes"')
if idx != -1:
    print("=== HTML Section ===")
    print(text[idx-200:idx+800].encode('ascii', 'ignore').decode())

idx2 = text.find('async function planRoute')
if idx2 != -1:
    print("\n=== JS Function ===")
    print(text[idx2:idx2+600].encode('ascii', 'ignore').decode())
