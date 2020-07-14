import json
d = {
    "uuid": "f7a54088-9860-458b-a723-8b9e577f0c8f",
    "name": "vm1",
    "memory": "2048mb"
}

with open('out1.json', 'w') as fout:
    fout.write(json.dumps(d))
with open('out2.json', 'w') as fout:
    fout.write(json.dumps(d, indent=2))  