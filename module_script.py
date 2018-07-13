import requests
import yaml

url = 'https://mbs.engineering.redhat.com/module-build-service/1/module-builds/?state=ready&per_page=100&verbose=True'
modules = []
with open('blacklist.yaml', 'r') as blacklist_file:
    blacklist = yaml.safe_load(blacklist_file)
blacklist_req = set(blacklist.get('requires', []))
blacklist_br = set(blacklist.get('buildrequires', []))

while True:
    response = requests.get(url).json()
    for module in response['items']:
        modulemd = module['modulemd']
        dependencies = modulemd['dependencies']
        module_br = set()
        module_req = set()
        for dependency in dependencies:
            module_br = module_br.union(set(dependency.get('buildrequires', {}).keys()))
            module_req = module_req.union(set(dependency.get('requires', {}).keys()))
        # compare sets, print out offending modules and add error message of why its an offender
        # specify buildrequires or requires
    if response['meta']['next']:
        url = response['meta']['next']
    else:
        break
