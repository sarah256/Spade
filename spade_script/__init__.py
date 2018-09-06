from __future__ import print_function
import yaml
import json
import sys
import logging

import gi
gi.require_version('Modulemd', '1.0')  # noqa
from gi.repository import Modulemd  # noqa

log = logging.getLogger('validate_modulemd')


def validate_modulemd(modulemd_file, module_name):
    with open('spade_script/blacklist.yaml', 'r') as blacklist_file_handler:
        blacklist = yaml.safe_load(blacklist_file_handler)
    with open(modulemd_file, 'r') as file_modulemd_handler:
        modulemd = yaml.safe_load(file_modulemd_handler)

    blacklist_req = set(blacklist.get('requires', []))
    blacklist_br = set(blacklist.get('buildrequires', []))
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
        print('\nThe module {0} has a buildrequires dependency on {1}\n'.format(
            module_name, ', '.join(str(x) for x in overlap_br)), file=sys.stderr)
    if overlap_req:
        print('\nThe module {0} has a requires dependency on {1}\n'.format(
            module_name, ', '.join(str(x) for x in overlap_req)), file=sys.stderr)
    if not overlap_br and not overlap_req:
        log.info('No Overlap Found')
        exit(1)
