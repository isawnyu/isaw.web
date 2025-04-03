Installing Anisble
------------------

We use the Plone Ansible playbooks to deploy this buildout, using a branch with
certbot SSL support. To get started run the setup script from this directory:

```
    $ ./setup_ansible.sh
```

That will checkout a custom branch of the Ansible playbooks, copy in the site
specific configuration, install Ansbile and required roles.

You will need a vault password file for decrypting passwords/tokens in a file at
`ansible-playbook/.vaultpass`

Adding Users
------------

Once ansible is setup locally, you can setup users on the server using:

```
    $ ansible-playbook add-users.yml
```

Setting up the Server
---------------------

ISAW uses apache rather than Plone's default nginx, so it needs some special setup to install apache and also clone a git repository with the static Kinik Hoyuk website:

```
    $ ansible-playbook apache.yml
```

There's a playbook to install a specified python version if different from
the OS version. The following command will intstall the python version specified
in `plone_python_version` using apt and the deadsnakes PPA:

```
    $ ansible-playbook install-python.yml
```

For Plone 5.2, python 3.8 is the default though it is not the OS install, so it's best to run this before running the Plone playbook. The standard Plone playbook is used to setup the server:

```
    $ ansible-playbook playbook.yml
```

There's also a playbook to setup a Python 2.7 + Plone 5.1 instance on the server
(in `/usr/local/plone-5.1/migration`) to aid in migration. This must be run after
the primary `playbook.yml`:

```
    $ ansible-playbook migration-plone.yml
```

And add and enable custom fail2ban setup (if `install_fail2ban` is enabled in
the group/host vars):
```
    $ ansible-playbook fail2ban.yml
```

You can also optionally enable a UFW firewall:

```
    $ ansible-playbook firewall.yml

```

You can install NYU required security monitoring services by using the nyu-security playbook:

```
    $ ansible-playbook nyu-security.yml

```


## Inventory

The default inventory file is `inventory.cfg`.
It defines both live and staging groups, as well as a combined group for encrypted secrets that are available to all groups.

There is a matching vbox-host.cfg that defines the same groups, but targets the vagrant virtualbox.
Usage: `ansible-playbook -i vbox-inventory.cfg -l live playbook.yml`

### Host and Group Variables

For each host in the inventory, it is possible to customize deployment some
variables using the files in `host_vars`. For example
`host_vars/custom_staging.yml` would contain host specific variables for the `custom_staging` server.

Similarly, deployment variables common across a group of servers can be
configured in `group_vars`. For example, `group_vars/staging.yml`
contains settings common to all servers in the staging group.
