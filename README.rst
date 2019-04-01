tequila-fab
===========

This is a Python package providing a library that can be imported
from `fabric3 <https://pypi.org/project/Fabric3/>`_ scripts to provide common implementations of
typical tasks for projects that are using
`tequila <https://github.com/caktus/tequila>`_ for provisioning and deploy.

License
-------

This Ansible role is released under the BSD License.  See the `LICENSE
<https://github.com/caktus/tequila-django/blob/master/LICENSE>`_ file for
more details.

Releases
--------

We attempt to not make changes that break backward-compatibility.
Nonetheless, you should *always* use a pinned version of this
repo to be safe.  Check the
`release history <RELEASES.rst>`_ before upgrading for
any notes or warnings.

Contributing
------------

If you think you've found a bug or are interested in contributing to
this project, check out `tequila-fab on Github
<https://github.com/caktus/tequila-fab>`_.

Development sponsored by `Caktus Consulting Group, LLC
<http://www.caktusgroup.com/services>`_.

Installation
------------

pip install into your virtualenv::

    $ pip install git+https://github.com/caktus/tequila-fab@X.Y.Z#egg=tequila-fab

Usage
-----

The simplest case is to just import everything from tequila_fab at the top of your
``fabfile.py``::

    # fabfile.py

    from tequila_fab import *

Then write some tasks to select environments, e.g.::

    from fabric.api import env, task

    @task
    def staging():
        """
        Usage: fab staging <tasks>
        """
        env.environment = 'staging'

These just need to set ``env.environment`` to the name of one of your
tequila environments.

Now users can use the tasks as documented in the reference below. You'd
likely start with::

    $ fab install_roles
    $ fab <ENVNAME> bootstrap

for new servers.  Then::

    $ fab <ENVNAME> deploy
    $ fab <ENVNAME> create_superuser:user@example.com

Subsequent deploys can optionally skip the initial provisioning tasks
by using::

    $ fab <ENVNAME> deploy:play=web

Most of these tasks end up invoking Ansible playbooks from
`tequila <https://github.com/caktus/tequila>`_, so be sure to
see the
`docs there <https://github.com/caktus/tequila/blob/master/docs/project_setup.rst>`_
for more information, and of course your own playbooks and
configuration in your project's ``deployment`` directory.

Task reference
--------------

(In alphabetical order.)

bootstrap
.........

Does the simplest possible install of Python v2 so that Ansible can
run from then on.

Use when the target servers might not even have Python installed.::

    $ fab <ENVNAME> bootstrap

check_role_versions
...................

Check that the roles required in requirements.yml are all installed
and at the right version. If any are not installed, install them.
If any are installed from Galaxy but at the wrong version, fail. If
any are installed locally rather than from Galaxy, fail, unless the
dev flag is set (see the `dev` task).

This gets run automatically before a deploy or bootstrap, so won't
often need to be run by itself.::

    $ fab check_role_versions

create_superuser
................

Create a superuser with no password (there's no way to pass a
new password to the createpassword command non-interactively).
Use password reset after creating the user.::

    $ fab <ENVNAME> create_superuser:<USERNAME>

For example::

    $ fab staging create_superuser:dpoirier@caktusgroup.com

deploy
......

Run an ansible deploy for an environment.

By default, runs the playbook *site* and deploys
the default branch for the specified environment. You
can override either of those by passing ``playbook`` or
``branch`` options.  Do not include ``.yml`` in the playbook
name.

.. note::

   The *site* playbooks does the whole provisioning and deploy.
   You can optionally speed up deploys that don't need to update
   software and configuration of the base server by using the
   *web* playbook, which just updates the web servers.

You can also set/override any Ansible variable by passing
the ``extra_vars`` option.  Here's the usage::

    $ fab <ENV> deploy[:playbook=NNNN][:extra_vars=aaa=1,bbb=2][:branch=xxx]

Some examples::

    $ fab staging deploy
    $ fab staging deploy:playbook=site
    $ fab staging deploy:branch=PRJ-9999
    $ fab staging deploy:playbook=site:extra_vars=gunicorn_num_workers=8

dev
...

Turn on 'dev' flag which can change the behavior of other tasks.

install_roles
.............

Run Ansible galaxy's role installer for the requirements in
``deployment/requirements.yml``.

.. warning::

    Ansible galaxy does *not* check version numbers.
    It only installs roles that are not installed already.
    So running ``install_roles`` is not enough to ensure your
    roles are up to date.

    You can run ``fab check_role_versions`` to see if
    versions are up to date.

    ``deploy`` and ``bootstrap`` also check and refuse to
    run if versions are wrong.

.. note::

    Ansible galaxy always installs roles into the first directory
    on your roles_path by default. Maybe install_roles ought to
    override that on the command line and always install to
    deployment/roles?
