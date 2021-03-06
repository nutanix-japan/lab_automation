import json
import os
import requests

def main():
    with open('poc19.json', 'r') as fin:
        text = fin.read()
    body = json.dumps(json.loads(text))
    response = requests.post('http://127.0.0.1:8000/api/public/foundation/v1/run', data=body)
    print(response.text)

if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    main()