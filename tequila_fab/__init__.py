"""
All tasks should have Usage: lines in their docstrings.
See existing tasks for examples.  This allows users
to see an overview of tasks by just running
``fab --list``.

Add tasks that should be exported to ``__ALL__``.
"""
import os

from fabric.api import env, local, require, task
from fabric.colors import red
from fabric.tasks import execute

from .ansible import check_role_versions, install_roles

#
# Initialize env flags
#
env.devflag = False

#
# KEEP TASKS IN ALPHABETICAL ORDER
#
__ALL__ = [
    'bootstrap',
    'check_role_versions',
    'create_superuser',
    'deploy',
    'install_roles',
]


#
# KEEP TASKS IN ALPHABETICAL ORDER
#
@task
def bootstrap():
    """
    Usage: fab <ENV> bootstrap
    """
    install_roles()
    execute(check_role_versions)
    deploy("bootstrap_python")
    deploy("site", extra_vars='{"unmanaged_users": [ubuntu]}')


@task
def create_superuser(email):
    """
    Usage: fab <ENV> create_superuser:dpoirier@caktusgroup.com

    Requires a create_superuser playbook in the ansible configuration.
    """
    require('environment')
    deploy('create_superuser', extra_vars={'EMAIL': email})
    print(red("YOU SHOULD NOW DO A PASSWORD RESET"))


@task
def deploy(play=None, extra_vars=None, branch=None, limit=None, verbose=None):
    """
    Usage: fab <ENV> deploy[:playbook=NNNN][:extra_vars=aaa=1,bbb=2][:branch=xxx]
    """
    require('environment')
    execute(check_role_versions)
    cmd = ["ansible-playbook",
           "-i deployment/environments/{env}/inventory".format(env=env.environment)]
    playbook = play or "site"
    cmd.append("deployment/playbooks/{playbook}.yml".format(playbook=playbook))
    if extra_vars:
        cmd.append("--extra-vars='{extra_vars}'".format(extra_vars=extra_vars))
    if branch:
        cmd.append("-e repo_branch=%s" % branch)
    if limit:
        cmd.append("-l %s" % limit)
    if verbose:
        cmd.append("-%s" % verbose)
    cmd.append("-e ansible_working_directory=%s" % os.getcwd())
    local(" ".join(cmd))


@task
def dev():
    """
    Usage: fab dev <other commands>

    Turns on 'dev' flag which may change behavior of other commands.
    """
    env.devflag = True


@task
def recreate_venv():
    """
    Usage: <ENV> fab recreate_venv

    Forces the virtualenv to be deleted and then deploys the web tasks
    so that a new virtualenv is created with a refreshed copy of the
    Python binary.
    """
    require('environment')
    deploy('web', extra_vars={'force_recreate_venv': True})
