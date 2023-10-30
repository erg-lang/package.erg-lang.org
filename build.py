import requests
import os

owner = 'erg-lang'
repo = 'package-index'
path = ''
token = os.getenv('ERG_GITHUB_TOKEN')
url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'Bearer {token}',
}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    for item in data:
        if item['type'] == 'dir':
            print(f"Directory: {item['name']}")
        else:
            print(f"File: {item['name']}")
else:
    print(f"Failed to fetch directory structure. Status code: {response.status_code}")
