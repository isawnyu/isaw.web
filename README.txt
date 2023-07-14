ISAW Website Buildout
=====================

Includes sources for the following addons:


 * isaw.theme - https://github.com/isawnyu/isaw.theme
 * isaw.facultycv - https://github.com/isawnyu/isaw.facultycv
 * isaw.register - https://github.com/isawnyu/isaw.register
 * isaw.exhibitions - https://github.com/isawnyu/isaw.exibitions

Take note that these are kept in their own seperate repositories and pulled
into the src/ directory automatically by the mr.developer buildout extension.

Fugue Icons
-----------

The icons used for the content types are (C) 2013 Yusuke Kamiyamane.
All rights reserved.
<http://p.yusukekamiyamane.com/>

These icons are licensed under a Creative Commons
Attribution 3.0 License.
<http://creativecommons.org/licenses/by/3.0/>

Getting Started
---------------

This buildout runs Plone 4.3.3, and expects Python 2.7 (2.7.8).  In order to
get started you must first ensure you have Python version 2.7 installed on
your OS.  You can first check your python version to see if it is already
installed before proceeding:

    python --version

Or you might have Python 2.7 installed under its own name:

    python2.7 --version

And then check if you've got virtualenv installed:

    virtualenv --version

Or

    virtualenv-2.7 --version

If you've got a Python 2.7 installed and virtualenv installed, you can
safely skip to "Library Dependencies".

On OS X
-------

On Mac OS X, assuming you have a XCode and a 3rd party package manager (either
Homebrew or MacPorts) and are not currently in an active Virtualenv (otherwise
`deactivate`).  For Homebrew:

    brew install python

for MacPorts

    sudo port install python27

Install virtualenv.  For Homebrew:

    pip install virtualenv

for

    sudo port install py27-setuptools py27-virtualenv

This will install a `virtualenv-2.7` command for creating Python 2.7 virtualenvs.


On Ubuntu
---------

You will need to install the python dev packages:

    sudo apt-get update
    sudo apt-get install python-dev python2.7-setuptools python-pip python-virtualenv


Library Dependencies
--------------------

To ensure all of Plone's functionality works out of the box, you'll want to install a couple support libraries:

With Homebrew:

    brew install libxml2 libxslt libjpeg
    brew link libxml2 libxslt libjpeg

or MacPorts:

    sudo port install libxml2 libxslt libjpeg

or Apt:

    sudo apt-get install libxml2-dev libxslt-dev libjpeg-dev


Python Virtualenv Setup
-----------------------

If Python 2.7 is your default python or you have a Python 2.7 specific
virtualenv command, then create your virtualenv:

    virtualenv[-2.7] py27-venv

If your Python 2.7 is not the default python in your path, then:

    export PATH_TO_PTYHON_27=`which python2.7`
    virtualenv --python $PATH_TO_PTYHON_27 py27-venv


Buildout
--------

Activate your new environment and clone the buildout:

    cd py27-venv
    source bin/activate
    git clone git@github.com:isawnyu/isaw.web.git

Then bootstrap and run your buildout:

    cd isaw.web
    python ./bootstrap.py
    bin/buildout -c development.cfg

If this build fails due to a C compiler "unknown arguments" error, you may
have a buggy XCode install.  Specifically there is a know issue with XCode
5.1+ running on OS X Mountain Lion (10.8.x).  The workaround is to set the
following shell environment variables before running `buildout`:

    export CFLAGS=-Qunused-arguments
    export CPPFLAGS=-Qunused-arguments

This should pull down additional repositories, install python dependencies,
and in the end create the scripts to run a local development version of the
ISAW site.


Supervisor
----------

The services (ZEO server and clients) for the site are run by a
"supervisor" process. On staging and production, supervisor is installed at
the OS level via Ansible. For local development, it's installed via buildout.
This will affect exactly how supervisorctl and supervisord commands are invoked.
For local development, you will use `bin/supervisord` and `bin/supervisorctl`,
whereas on staging and production you'll invoke the executables from the system
PATH (and use sudo): `sudo supervisord` and `sudo supervisorctl`.

The example below assume you're working locally.

To start supervisor for the first time run:

    bin/supervisord

This will start the supervisor and the Zeoserver, but not the zope clients by default

If you need to stop the supervisor, run:

    bin/supervisorctl shutdown


Initial Admin User
------------------

You can create and/or set an Admin user password:

    bin/client1 adduser <name> <password>


Startup
-------

To run the local zeo client in development mode, you can start it up in
foreground mode:

    bin/client1 fg

You can now connect to the site at:

    http://127.0.0.1:8081/

Which should show you a button for creating a new Plone site.  You'll want to
create a new site and apply the isaw.policy default profile by checking the
corresponding checkbox. Having done so, you'll see the unthemed Plone site. 
To see the fully themed site, replace "127.0.0.1" with "localhost" in your 
browser's location bar, thus:

    http://localhost:8081/

The supervisor can also be used to run the Zeo clients in the background:

    bin/supervisorctl start client1
    bin/supervisorctl start client2


Development
-----------

You can update project sources by running:

    bin/develop up

Each in-development add-on package lives in a directory inside of `src/` and
is its own git repository.

And you can update the buildout itself with:

    git pull origin master
    bin/buildout -c development.cfg


Branches
--------

The primary buildout branch is currently `master`.

We want to develop all new features on distinct feature branches.  These
branches will be merged as needed to a separate `staging` branch for testing.
This process will allow for multiple features at different stages of readiness
to be tested on the staging server, and then deployed individually to
production as they are ready.  All feature branches should be branched from
the master branch, and then merged into the `staging` branch when ready for
testing. Once tested and ready for deploy the feature branch should be merged
directly into the master branch.

The `staging` branch would be branched from the master and periodically
updated with merged changes from master.  The `staging` branch should – in
general – never be modified directly or merged into other branches.  It should
be considered a repository for merges from feature branches and the master.
Small fixes should be made on the master branch or on a separate bugfix
branch, then merged to staging for testing, rather than made directly on
staging.

This strategy applies to the `master` branches of custom add-ons as well.

The following ASCII diagram attempts to illustrate the branching and merging
process::


    master
       |
       |----------------------------> staging
       |                                 |
       |-------> feature1                |
       |             |                   |
       |<------------|------------------>|
       |                                 |--> deploy
       |-------> feature2                |
       |             |                   |
       |             |                   |
       |             |                   |
       |             |                   |
       |             |                   |
       |             |------------------>|
       |             |                   |--> deploy
       |             |                   |
       |             |                   |
       |             |                   |
       |<------------|------------------>|
       |                                 |--> deploy
       |
       |--> deploy
