import json

with open('input.json') as fin:
    text = fin.read()

d = json.loads(text)
print(d)
print()
print(d['children'][0]['name'])
