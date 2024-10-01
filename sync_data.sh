#!/bin/bash
sudo chown -R plone_buildout:plone_group var
sudo chmod -R ug+rwX,o-rwx var
rsync -rloDzP isaw.nyu.edu:/usr/local/plone-4.3/primary/var/filestorage var
rsync -rloDzP isaw.nyu.edu:/usr/local/plone-4.3/primary/var/blobstorage var
