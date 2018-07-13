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
        modulemd = yaml.safe_load(module['modulemd'])
        dependencies = modulemd['dependencies']
        module_br = set()
        module_req = set()
        for dependency in dependencies:
            module_br = module_br.union(set(dependency.get('buildrequires', {}).keys()))
            module_req = module_req.union(set(dependency.get('requires', {}).keys()))
        overlap_br = set(blacklist_br).intersection(set(module_br))
        overlap_req = set(blacklist_req).intersection(set(module_req))
        if overlap_br:
            modules.append(module)
            raise RuntimeError('The module {0} with the ID {1} has a buildrequires dependency on {2}').format(
                module['name'], module['id'], ', '.join(str(x) for x in overlap_br))
        if overlap_req:
            modules.append(module)
            raise RuntimeError('The module {0} with the ID {1} has a requires dependency on {2}').format(
                module['name'], module['id'], ', '.join(str(x) for x in overlap_br))
    if response['meta']['next']:
        url = response['meta']['next']
    else:
        break
