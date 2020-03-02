from __future__ import print_function
import yaml
import json
import sys
import logging

import gi
gi.require_version('Modulemd', '2.0')  # noqa
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
        mmd = Modulemd.ModuleStream.read_string(modulemd, True)
        mmd.upgrade(Modulemd.ModuleStreamVersionEnum.TWO)
    except Exception:
        raise ValueError('Invalid modulemd')
    dependencies = mmd.get_dependencies()

    module_br = set()
    module_req = set()
    overlap_br = None
    overlap_req = None
    for dependency in dependencies:
        # Find if any buildtime dependencies are blacklisted
        module_br = module_br.union(set(dependency.get_buildtime_modules()))
        overlap_br = set(blacklist_br).intersection(set(module_br))
        # Find if any runtime dependencies are blacklisted
        module_req = module_req.union(set(dependency.get_runtime_modules()))
        overlap_req = set(blacklist_req).intersection(set(module_req))

    if overlap_br:
        print('\nThe module {0} has a build-time dependency on {1}\n'.format(
            module_name, ', '.join(str(x) for x in overlap_br)), file=sys.stderr)
    if overlap_req:
        print('\nThe module {0} has a runtime dependency on {1}\n'.format(
            module_name, ', '.join(str(x) for x in overlap_req)), file=sys.stderr)
    if not overlap_br and not overlap_req:
        print('\nNo Overlap found for {0}\n'.format(module_name), file=sys.stderr)
