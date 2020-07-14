import requests

response = requests.get('http://www.google.co.jp')
print(f'response.ok : {response.ok}')
print(f'response.status_code : {response.status_code}')
text = response.text
print(f'response.text : {text[:100] if len(text) > 100 else text}')
print(f'response.json() : {response.json()}')