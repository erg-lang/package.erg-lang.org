import requests
import os
import jinja2
import base64
import shutil

import erg_compiler

class License(str):
    def url(self):
        match self:
            # TODO: multiple licenses
            case "MIT" | "MIT OR Apache-2.0" | "MIT or Apache-2.0":
                return "https://opensource.org/licenses/MIT"
            case "Apache-2.0" | "Apache-2.0 OR MIT" | "Apache-2.0 or MIT":
                return "https://opensource.org/licenses/Apache-2.0"
            case "BSD-3-Clause":
                return "https://opensource.org/licenses/BSD-3-Clause"
            case "BSD-2-Clause":
                return "https://opensource.org/licenses/BSD-2-Clause"
            case "MPL-2.0":
                return "https://opensource.org/licenses/MPL-2.0"
            case "GPL-3.0":
                return "https://opensource.org/licenses/GPL-3.0"
            case "AGPL-3.0":
                return "https://opensource.org/licenses/AGPL-3.0"
            case "CC0" | "CC0-1.0":
                return "https://creativecommons.org/publicdomain/zero/1.0/"
            case _:
                return ""

class Package:
    namespace: str
    name: str
    version: str
    description: str | None
    tags: list[str]
    license: License
    repository: str | None

    def __init__(self, namespace, name, version, description, tags, license, repository):
        self.namespace = namespace
        self.name = name
        self.version = version
        self.description = description
        self.tags = tags
        self.license = License(license)
        self.repository = repository

    def __repr__(self):
        return f'Package({self.name}, {self.version}, "{self.description}", {self.tags}, {self.license}, {self.repository})'

pkgs = []

owner = 'erg-lang'
repo = 'package-index'
token = os.getenv('ERG_GITHUB_TOKEN')
devs_url = f'https://api.github.com/repos/{owner}/{repo}/contents/developers'
cert_url = f'https://api.github.com/repos/{owner}/{repo}/contents/certified'
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'Bearer {token}',
}

def add_package(namespace, url, pkg):
    if pkg['type'] == 'dir':
        package_er = f'{url}/{pkg["name"]}/package.er'
        resp = requests.get(package_er, headers=headers)
        pkg_data = resp.json()
        decoded_content = base64.b64decode(pkg_data['content']).decode('utf-8')
        pkg_module = erg_compiler.exec(decoded_content)
        pkg = Package(
            namespace,
            pkg_module.name,
            pkg_module.version,
            pkg_module.__dict__.get('description', ''),
            pkg_module.__dict__.get('tags', []),
            pkg_module.license,
            pkg_module.__dict__.get('repository'),
        )
        pkgs.append(pkg)

response = requests.get(devs_url, headers=headers)
if response.status_code == 200:
    developers = response.json()
    for developer in developers:
        if developer['type'] == 'dir':
            dev = developer['name']
            dev_url = f'{devs_url}/{dev}'
            resp = requests.get(dev_url, headers=headers)
            for pkg in resp.json():
                add_package(dev, dev_url, pkg)
else:
    print(f"Failed to fetch directory structure. Status code: {response.status_code}")

response = requests.get(cert_url, headers=headers)
if response.status_code == 200:
    certified = response.json()
    for pkg in certified:
        print("pkg:", pkg)
        # add_package(cert_url, pkg)
else:
    print(f"Failed to fetch directory structure. Status code: {response.status_code}")

featured = pkgs[:5]
new = pkgs[:5]

if not os.path.exists('docs'):
    os.makedirs('docs')
shutil.copyfile('style.css', 'docs/style.css')
shutil.copyfile('script.js', 'docs/script.js')
shutil.copyfile('search.js', 'docs/search.js')
shutil.copyfile('package-policy.html', 'docs/package-policy.html')
shutil.copyfile('privacy-policy.html', 'docs/privacy-policy.html')
shutil.copyfile('security.html', 'docs/security.html')

env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
template = env.get_template("template.html")
template.stream(featured=featured, new=new).dump("docs/index.html")
template = env.get_template("template_all.html")
template.stream(pkgs=pkgs).dump("docs/all.html")

for pkg in pkgs:
    if not os.path.exists(f'docs/{pkg.namespace}'):
        os.makedirs(f'docs/{pkg.namespace}')
        # shutil.copyfile('style.css', f'docs/{pkg.namespace}/style.css')
        # shutil.copyfile('script.js', f'docs/{pkg.namespace}/script.js')
    template = env.get_template("template_package.html")
    template.stream(pkg=pkg).dump(f"docs/{pkg.namespace}/{pkg.name}.html")
