#!/bin/bash
sudo chmod -R g+rwX /usr/local/plone-5.2/zeoserver/var
sudo chown -R plone_daemon:plone_group /usr/local/plone-5.2/zeoserver/var
sudo rsync -aP var/filestorage /usr/local/plone-5.2/zeoserver/var
sudo rsync -aP var/blobstorage /usr/local/plone-5.2/zeoserver/var
sudo rsync -aP var/solr /usr/local/plone-5.2/zeoserver/var
