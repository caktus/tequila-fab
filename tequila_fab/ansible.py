import configparser
import functools
import os
import os.path
import sys
from typing import Optional, List

import yaml
from fabric.api import local
from fabric.colors import red, green, yellow
from fabric.decorators import task


@functools.lru_cache(maxsize=1)
def find_ansible_config_file() -> Optional[str]:
    """
    Return path to the ansible config file that ansible would use,
    or None if no config file found.

    Ansible uses the first config file it finds on this list:

    ANSIBLE_CONFIG (an environment variable)
    ansible.cfg (in the current directory)
    .ansible.cfg (in the home directory)
    /etc/ansible/ansible.cfg
    """
    possible_paths = [
        os.environ.get('ANSIBLE_CONFIG', False),
        'ansible.cfg',
        os.path.join(os.environ['HOME'], '.ansible.cfg'),
        '/etc/ansible/ansible.cfg',
    ]
    for path in possible_paths:
        if path and os.path.exists(path):
            return os.path.abspath(path)
    return None


@functools.lru_cache(maxsize=1)
def get_ansible_configuration() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config['DEFAULTS'] = {
        'roles_path': os.path.join(os.environ['HOME'], '/.ansible/roles') + ':/usr/share/ansible/roles:/etc/ansible/roles'
    }

    path = find_ansible_config_file()
    if path is not None:
        config.read(path)
    return config


@functools.lru_cache(maxsize=1)
def get_roles_path() -> List[str]:
    """
    Return list of directories where Ansible will look for roles
    """
    return get_ansible_configuration()['defaults']['roles_path'].split(':')


@task
def install_roles():
    """
    Usage: fab install_roles
    """
    local('ansible-galaxy install -i -r deployment/requirements.yml')


def find_install_role(rolename) -> Optional[str]:
    """
    Returns path of directory where role is installed,
    or None.
    """
    for path in get_roles_path():
        dir = os.path.join(path, rolename)
        if os.path.isdir(dir):
            return dir


def req_name(req) -> str:
    """
    Return name of the role in the given roles requirements entry
    """
    return req.get('name', req['src'])


@task
def check_role_versions():
    """
    Usage: fab check_role_versions

    Fails if the exact versions of roles specified in deployment/requirements.yml
    are not installed.
    """

    okay = True  # False if we've spotted any problems
    bad = []  # Paths to where missing roles should be installed, or where bad version roles are installed
    requirements = yaml.load(open("deployment/requirements.yml"))
    requirements = sorted(requirements, key=req_name)
    for req in requirements:
        name = req_name(req)
        install_dir = find_install_role(name)
        if not install_dir:
            okay = False
            print(red("ERROR: role %s not installed" % (name,)))
            continue
        meta_path = os.path.join(install_dir, 'meta/.galaxy_install_info')
        if os.path.exists(meta_path):
            meta = yaml.load(open(meta_path))
            if meta['version'] != req['version']:
                print(red("ERROR: role %s at %s is version %s, should be version %s" % (
                    name,
                    install_dir,
                    meta['version'],
                    req['version']
                )))
                okay = False
                bad.append(install_dir)
            else:
                print(green("GOOD:  role %s %s at %s" % (name, meta['version'], install_dir)))
        else:
            # User must have installed this locally, don't check version
            print(yellow("SKIP:  role %s at %s appears to have been locally installed" % (name, install_dir)))
    if not okay:
        print(red("Ansible galaxy role requirements are not satisfied, quitting.  The simplest fix is to delete "
                  "the roles that have wrong versions, then run ``fab install_roles`` again."))
        if bad:
            print("E.g.")
            print("$ rm -r %s" % " ".join(badname for badname in bad))
        sys.exit(1)
