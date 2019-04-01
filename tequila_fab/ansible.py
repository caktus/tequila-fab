import configparser
import functools
import os
import os.path

# FIXME: when we drop Python 2 support, change the comment-style type annotations to Python 3 style.

import yaml
from fabric.api import local
from fabric.colors import red, green, yellow
from fabric.decorators import task
from fabric.tasks import execute
from fabric.utils import abort


@functools.lru_cache(maxsize=1)
def find_ansible_config_file():  # type: () -> Optional[str]
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
def get_ansible_configuration():  # type: () -> configparser.ConfigParser
    config = configparser.ConfigParser()
    config['DEFAULTS'] = {
        'roles_path': os.path.join(os.environ['HOME'], '/.ansible/roles') + ':/usr/share/ansible/roles:/etc/ansible/roles'
    }

    path = find_ansible_config_file()
    if path is not None:
        config.read(path)
    return config


@functools.lru_cache(maxsize=1)
def get_roles_path():  # type: () -> List[str]
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


def find_install_role(rolename):  # type: str -> Optional[str]
    """
    Returns path of directory where role is installed,
    or None.
    """
    for path in get_roles_path():
        dir = os.path.join(path, rolename)
        if os.path.isdir(dir):
            return dir


def req_name(req):  # type: Dict -> str
    """
    Return name of the role in the given role's requirements entry
    """
    return req.get('name', req['src'])


@task
def check_role_versions():  # type: () -> None
    """
    Usage: fab check_role_versions

    If the wrong versions of any roles are installed, per deployment/requirements.yml,
    fail.

    If any required roles are not installed, install them.

    If env.devflag is true, warns but ignores any locally installed roles. Otherwise,
    locally installed roles are a fatal error. See the `dev` task
    to set env.devflag.
    """

    okay = True  # False if we've spotted any problems
    bad = []  # Paths to where missing roles should be installed, or where bad version roles are installed
    requirements = yaml.load(open("deployment/requirements.yml"))
    requirements = sorted(requirements, key=req_name)
    requirements_to_install = False
    for req in requirements:
        name = req_name(req)
        install_dir = find_install_role(name)
        if not install_dir:
            print(yellow("WARNING: role %s not installed" % (name,)))
            requirements_to_install = True
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
            if env.devflag:
                print(yellow("SKIP:  role %s at %s appears to have been locally installed" % (name, install_dir)))
            else:
                okay = False
                print(red("ERROR:  role %s at %s appears to have been locally installed, will not continue" % (name, install_dir)))
                print(red("To ignore this error, add 'dev' argument to fab command before this"))

    if requirements_to_install and okay:
        execute(install_roles)

    if not okay:
        print(red("Ansible galaxy role requirements are not satisfied, quitting.  The simplest fix is to delete "
                  "the roles that have wrong versions, then run ``fab install_roles`` again."))
        if bad:
            print("E.g.")
            print("$ rm -r %s" % " ".join(badname for badname in bad))
        abort('check_installed_roles failed')
