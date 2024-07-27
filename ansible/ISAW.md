# ISAW Ansible playbook

Ansible playbooks meant to be sufficient to build or rebuild a server with
minimal preparation.

These do not handle live data transfer.

## Prerequisites

Ansible >= 2.1.

Ubuntu 16.04 server and an ssh login with full sudo. The server must have the
following packages installed::

* python
* aptitude

Use the following commands to install them::

    sudo apt-get update
    sudo apt-get install aptitude python

You may also need to ensure the apt src repositories are available by
uncommenting apt-src locations in `/etc/apt/sources.list`.

Install required ansible roles::

    ansible-galaxy -p roles -r requirements.yml install

Create a `vault-pass` file with the password for decrypting secret keys, etc.

To deploy run `ansible-playbook` targetting specific servers or groups:

        ansible-playbook -l staging playbook.yml

### Warning

Ansible requires that the target server have a recent Python 2.x on the server. Newer platforms (like Ubuntu Xenial and later) may not have this activated on pristine new machines.

If you get connection errors from Ansible, check the remote machine to make sure Python 2.7 is available.
`which python2.7` will let you know.
If it's missing, use your package manager to install it.

On Ubuntu Xenial (16.0.4 LTS) or Bionic (18.0.4 LTS), `sudo apt-get install -y python2.7-dev` will do the trick.

ansible-galaxy -p roles install -r install_roles.yml

## Inventory


The default inventory file is `inventory.cfg`.
It defines both live and staging groups.

There is a matching vbox-host.cfg that defines the same groups, but targets the vagrant virtualbox.
Usage: `ansible-playbook -i vbox-host.cfg -l live playbook.yml`

### Host and Group Variables

For each host in the inventory, it is possible to customize deployment some
variables using the files in `host_vars`. For example
`host_vars/custom_staging.yml` would contain host specific variables for the `custom_staging` server.

Similarly, deployment variables common across a group of servers can be
configured in `group_vars`. For example, `group_vars/staging.yml`
contains settings common to all servers in the staging group.
