import json
with open('clientes.json', 'r', encoding='utf-16') as f:
    data = json.load(f)
print(data)
