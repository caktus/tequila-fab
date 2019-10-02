Releases
========

* 0.0.8, 2019-10-02

  * Add a new "verbose" option to the deploy task to allow passing
    verbosity levels, e.g. ``v``, ``vv``, etc.

* 0.0.7, 2019-09-06

  * Add a new "limit" option to the deploy task to pass a "--limit" through
    to ansible-playbook.

* 0.0.6, 2019-08-06

  * New task 'recreate_venv' allows virtualenv to be recreated. Requires
    tequila-django >= 0.9.24.

* 0.0.5, 2019-06-17

  * Fix version number in setup.py.

* 0.0.4, 2019-04-24

  * Undo change to how unmanaged users are set on bootstrap deploy that
    shouldn't have been in the last release.

* 0.0.3, 2019-04-23

  * If a required role is not installed, check_installed_roles installs it.
  * New task 'dev' sets a 'dev' flag that can affect behavior of other tasks.
  * If a role is installed locally instead of from Galaxy, check_installed_roles
    fails unless the 'dev' flag is set.

* 0.0.2, 2019-01-17

  * Add Python 2.7 support.
  * Deploys default to using the "site" playbook (was "web").
  * Add "ansible_working_directory" to variables defined on deploy.
  * Don't pass "--user" to ansible-playbook. It's up to the project
    inventory and variables to know what the right user is for ssh'ing
    to each remote system.

* 0.0.1, 2018-11-07: initial release
