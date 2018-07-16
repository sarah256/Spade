from __future__ import print_function
import sys
import requests
import yaml
import json

import gi
gi.require_version('Modulemd', '1.0')  # noqa
from gi.repository import Modulemd  # noqa


url = 'https://mbs.engineering.redhat.com/module-build-service/1/module-builds/?state=ready&per_page=100&verbose=True'
with open('blacklist.yaml', 'r') as blacklist_file:
    blacklist = yaml.safe_load(blacklist_file)
modules = []
blacklist_req = set(blacklist.get('requires', []))
blacklist_br = set(blacklist.get('buildrequires', []))

while True:
    response = requests.get(url).json()
    for module in response['items']:
        modulemd = yaml.safe_load(module['modulemd'])
        modulemd = json.dumps(modulemd)
        try:
            mmd = Modulemd.Module().new_from_string(modulemd)
            mmd.upgrade()
        except Exception:
            raise ValueError('Invalid modulemd')
        mmd_file = mmd.dumps()
        mmd = yaml.load(mmd_file)
        dependencies = mmd['data']['dependencies']
        module_br = set()
        module_req = set()
        for dependency in dependencies:
            if 'buildrequires' in dependency.keys():
                module_br = module_br.union(set(dependency['buildrequires']))
                overlap_br = set(blacklist_br).intersection(set(module_br))
            if 'requires' in dependency.keys():
                module_req = module_req.union(set(dependency['requires']))
                overlap_req = set(blacklist_req).intersection(set(module_req))
        if overlap_br:
            modules.append(module)
            print('\nThe module {0} with the ID {1} has a buildrequires dependency on {2}\n'.format(
                module['name'], module['id'], ', '.join(str(x) for x in overlap_br)), file=sys.stderr)
        if overlap_req:
            modules.append(module)
            print('\nThe module {0} with the ID {1} has a requires dependency on {2}\n'.format(
                module['name'], module['id'], ', '.join(str(x) for x in overlap_req)), file=sys.stderr)
    if response['meta']['next']:
        url = response['meta']['next']
    else:
        break

if modules:
    sys.exit(1)
