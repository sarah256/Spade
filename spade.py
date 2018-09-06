#!/usr/bin/python

import argparse
import logging
import os
import json
import pprint
import requests
import tempfile

from pygit2 import clone_repository, Oid

import spade_script


log = logging.getLogger('root')

DATAGREPPER_URL = 'https://datagrepper.engineering.redhat.com/id'
GIT_URL = 'git://pkgs.devel.redhat.com/modules/'


def get_message(args):
    """ Inspired from
        https://gitlab.cee.redhat.com/devops/release-driver/blob/master/release-driver.py
    """
    if args.id_or_url:
        try:
            if args.id_or_url.startswith(('http://', 'https://')):
                response = requests.get(args.id_or_url)
            else:
                datagrepper_params = {'id': args.id_or_url,
                                      'is_raw': 'true',
                                      'size': 'extra-large'}
                response = requests.get(DATAGREPPER_URL, params=datagrepper_params)

            full_url = response.url
            response.raise_for_status()
            msg = response.json()
        except Exception:
            log.exception("Couldn't get/load message from URL: %s" %
                          full_url)
            raise

    else:
        try:
            msg = json.loads(os.environ['CI_MESSAGE'])
        except Exception:
            log.error("Failed to load message. The env was: %s" % pprint.pformat(os.environ))
            raise

    log.info("Handling message ID: %s", msg.get("message_id"))
    log.debug("Message content:\n%s", json.dumps(msg, indent=4, sort_keys=True))
    msg = msg.get('msg', msg)
    return msg


def clone_modulemd_repo(msg):
    tmp = tempfile.mkdtemp(prefix='{0}-'.format(msg["repo"]), dir='/var/tmp')

    repo = clone_repository(GIT_URL + msg["repo"], tmp, checkout_branch=msg["branch"])
    log.info("Cloning repo {0} to \'/var/temp\'".format(msg["repo"]))

    repo.set_head(Oid(hex=msg["rev"]))
    log.info("Set head to commit hash {0}".format(msg["rev"]))

    return tmp


def main(args=None):
    msg = get_message(args)
    filenames = msg["stats"]["files"]
    if not filenames:
        log.info("No files were changed! Skipping...")
        exit(1)

    for filename in filenames.keys():
        if filename.endswith(".yaml"):
            modulemd_file = clone_modulemd_repo(msg) + '/{0}.yaml'.format(msg["repo"])
            log.info("Comparing {0} file to blacklist!".format(modulemd_file))
            spade_script.validate_modulemd(modulemd_file, msg["repo"])
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Release Driver')
    parser.add_argument('-d', '--debug', default=False, action='store_true',
                        help='Show debug information')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='Be more verbose')
    parser.add_argument('id_or_url', metavar='MESSAGE_ID_OR_URL', type=str,
                        nargs='?',
                        help='Message ID or Datagrepper URL. If not supplied, '
                             'CI_MESSAGE environment variable is examined for '
                             'a dist-git commit message with ModuleMD change.')
    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)
    elif args.verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARN)
    logging.basicConfig()

    main(args)
