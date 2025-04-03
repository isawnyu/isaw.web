#!/bin/bash
if [ ! -d ansible-playbook ]; then
    git clone -b certbot-ssl https://github.com/plone/ansible-playbook.git
fi
cd ansible-playbook
ln -sf ../ansible.cfg ../add-users.yml ../inventory.cfg ../local-configure.yml ../migration-plone.yml ../install-python.yml ../plone_user_keys ../group_vars ../host_vars ../fail2ban.yml ../apache.yml ../files ../requirements.yml ../saml_keys ../templates ../nyu-security.yml .
pip install cryptography
pip install -U ansible~=2.10
ansible-galaxy install -r requirements.yml
