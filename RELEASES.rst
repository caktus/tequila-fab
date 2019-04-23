Releases
========

* next

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
