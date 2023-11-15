import requests
import os
import jinja2
import base64

import erg_compiler

class Package:
    name: str
    version: str
    description: str

    def __init__(self, name, version, description):
        self.name = name
        self.version = version
        self.description = description

    def __repr__(self):
        return f'Package({self.name}, {self.version}, "{self.description}")'

featured = []
new = []

owner = 'erg-lang'
repo = 'package-index'
path = ''
token = os.getenv('ERG_GITHUB_TOKEN')
devs_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}/developers'
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'Bearer {token}',
}
response = requests.get(devs_url, headers=headers)

if response.status_code == 200:
    developers = response.json()
    for developer in developers:
        if developer['type'] == 'dir':
            dev = developer['name']
            dev_url = f'{devs_url}/{dev}'
            resp = requests.get(dev_url, headers=headers)
            for pkg in resp.json():
                if pkg['type'] == 'dir':
                    package_er = f'{dev_url}/{pkg["name"]}/package.er'
                    resp = requests.get(package_er, headers=headers)
                    pkg_data = resp.json()
                    decoded_content = base64.b64decode(pkg_data['content']).decode('utf-8')
                    pkg_module = erg_compiler.exec_module(decoded_content)
                    pkg = Package(pkg_module.name, pkg_module.version, pkg_module.description)
                    featured.append(pkg)
                    new.append(pkg)
else:
    print(f"Failed to fetch directory structure. Status code: {response.status_code}")

env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
template = env.get_template("template.html")
template.stream(featured=featured, new=new).dump("test.html")
