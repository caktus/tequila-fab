import os.path
import sys

import yaml
from fabric.api import local, task
from fabric.decorators import task


@task
def install_roles():
    """
    Usage: fab install_roles
    """
    local('ansible-galaxy install -i -r deployment/requirements.yml')


@task
def check_role_versions():
    """
    Usage: fab check_role_versions

    Fails if the exact versions of roles specified in deployment/requirements.yml
    are not installed.
    """
    # TODO: Read ansible config for roles path
    # TODO: check all directories on roles path

    okay = True  # False if we've spotted any problems
    bad = []  # Paths to where missing roles should be installed, or where bad version roles are installed
    requirements = yaml.load(open("deployment/requirements.yml"))
    for req in requirements:
        name = req.get('name', req['src'])
        rolepath = 'deployment/roles/%s' % name
        if not os.path.isdir(rolepath):
            okay = False
            print("ERROR: role %s not installed (%s not found or is not directory)" % (name, rolepath))
            continue
        metapath = os.path.join(rolepath, 'meta/.galaxy_install_info')
        if os.path.exists(metapath):
            meta = yaml.load(open(metapath))
            if meta['version'] != req['version']:
                print("ERROR: role %s is version %s, should be version %s" % (
                    name,
                    meta['version'],
                    req['version']
                ))
                okay = False
                bad.append(rolepath)
        else:
            # User must have installed this locally, don't check version
            print("Skipping version check for %s because %s not found, probably locally installed" % (name, metapath))
    if not okay:
        print("Ansible galaxy role requirements are not satisfied, quitting.  The simplest fix is to delete "
              "the roles that have wrong versions, then run ``fab install_roles`` again.")
        if bad:
            print("E.g.")
            print("$ rm -r %s" % " ".join(badname for badname in bad))
        sys.exit(1)
