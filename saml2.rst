******************************
Setup for saml2 authentication
******************************

To use the `collective.saml2 <https://github.com/collective/collective.saml2>`_
PAS plugin, a few things must be in place first.

**OS Packages:**

* libxml2
* libxslt
* libxmlsec1
* openssl

**Python Packages:**

* lxml
* dm.xmlsec.binding
* PyXB

Under Linux, it is enough to install the correct system packages. If the
buildout has already been run, you will need to remove the ``lxml`` package and
re-run buildout.  This will allow ``lxml`` to be built with awareness of the
proper C-library bindings (and get ``dm.xmlsec.binding`` built with awareness
of the proper ``lxml``).

However, under OS X the system versions of libxml2 and libxslt are not usable.
You'll need to do extra work to get appropriate versions of the packages
installed and to get the Python installations of ``lxml``, ``PyXB`` and
``dm.xmlsec.binding`` to see them.

Ubuntu Only
===========

Install the required system packages::

    $ sudo apt-get install openssl libxml2 libxml2-dev libxslt1.1 libxslt1-dev libxmlsec1 libxmlsec1-dev

OS X Only
=========

1. Install the system level software::

    $ brew install libxml2 libxslt libxmlsec1 openssl

.. note:: Please note that with the exception of libxmlsec1 these are all keg-only.
          Make note of the installation directory (It should be /usr/local/Cellar/<packagename>)

          Recent versions of Homebrew will add a version-specific subdirectory, and place
          the "keg"'s /bin directory inside this subdirectory. You will need the full path
          to the /bin directories in step 3 below, as in the example shown in that step.

2. Create a virtual environment, specifying a current Python 2.7.x::

    $ virtualenv --python /usr/local/bin/python2.7 saml2env
    $ cd saml2env
    $ bin/python -m pip install -U pip setuptools

3. Temporarily set your system PATH to include the installed packages' config
   binaries (**do not do this permanently**)::

    $ export BASE=/usr/local/Cellar  # this is the install directory from step 1 above
    $ export PATH=$BASE/libxml2/<version_dir>/bin:$BASE/libxslt/<version_dir>bin:$BASE/libxmlsec1/<version_dir>bin:$PATH

    An example using version directories which may not match your own:

    ``export PATH=$BASE/libxml2/2.9.7/bin:$BASE/libxslt/1.1.32/bin:$BASE/libxmlsec1/1.2.26/bin:$PATH``

4. Confirm that the necessary binaries are available in your PATH by running
   the following commands::

    $ xml2-config
    Usage: xml2-config [OPTION]
    ...

    $ xslt-config
    Usage: xslt-config [OPTION]...
    ...

    $ xmlsec1-config
    Usage: xmlsec1-config [OPTION]...
    ...

   If any of these fail to echo a usage summary, then something is not right
   with either your PATH or the installation of the system packages themselves.

5. pip install the Python packages required, specifying the versions used
   in versions.cfg::

    $ bin/pip install lxml==3.2.5
    $ bin/pip install pyxb==1.2.5
    $ bin/pip install dm.xmlsec.binding==1.3.2
    $ bin/pip install cssselect==1.0.0

All Systems
===========

On both systems, you'll need to run the buildout.

If the buildout has been run before
-----------------------------------

You must not use a version of ``lxml`` that has been built prior to having all
the critical C-bindings in place. If you have already run buildout you must
remove the ``lxml`` package from your egg cache so that it will be rebuilt (on
Ubuntu) or skipped (on OS X).

1. Find the location of your installed ``lxml`` package::

    $ cd /path/to/isaw.web
    $ cat bin/client1 | grep lxml
    /path/to/buildout/cache/lxml-2.3.6-py2.7-macosx-10.10-intel.egg

2. Delete the package::

    $ rm -rf /path/to/buildout/cache/lxml-2.3.6-py2.7-macosx-10.10-intel.egg

3. Delete other artifacts to force full re-build::

    $ rm .installed.cfg 

In all cases
------------

Bootstrap the buildout, specifying zc.buildout version 1.7.1::

      OS X: $ /path/to/saml2env/bin/python bootstrap.py -v 1.7.1 -c buildout.cfg
    Ubuntu: $ python bootstrap.py -v 1.7.1 -c buildout.cfg

Run the buildout::

    $ bin/buildout -v -c buildout.cfg

You should see a confirmation in the logging output that ``lxml``, ``pyxb``, 
``dm.xmlsec.binding``, and ``cssselect`` are treated as already installed::

    ...
    Egg from site-packages: dm.xmlsec.binding 1.3.2
    Egg from site-packages: PyXB 1.2.5
    ...


Troubleshooting Setup
=====================

Once you've installed everything as directed, you should be able to test the
installation of dm.xmlsec.binding. Start by firing up the ``zopepy`` interpreter::

    $ bin/zopepy

Next, attempt to import and initialize the ``dm.xmlsec.binding`` package:

.. code-block:: python

    >>> import dm.xmlsec.binding as xmlsec
    >>> xmlsec.initialize()
    >>>

If you receive an error regarding missing Symbols from lxml.etree, then there
is a problem with how lxml was built. It does not have access to the
appropriate headers from the C libraries beneath it.  Uninstall it and try
again, ensuring that the paths to ``xml2-config``, ``xslt-config``, and
``xmlsec1-config`` are accessible (and found) when you install ``lxml``.


PAS Plugin Installation
=======================

The `instructions for setting up the plugin <https://github.com/collective/collective.saml2>`_
are a bit incomplete with respect to getting the service working with an
external IdP (Identity Provider) like NYU's SSO.

`Step 1: Setup your authority <https://github.com/collective/collective.saml2#step-1-setup-your-authority>`_
------------------------------------------------------------------------------------------------------------

There are a few additional notes for this first step in the plugin documentation.

1. Despite the note that no certificate or key are required for setting up a
   Service Provider, the NYU IdP would like very much for there to be one
   present. The .pem component of the certificate can be extracted from
   /conf/shibboleth_metadata.xml, and then adding ``-----BEGIN CERTIFICATE-----``
   and ``-----END CERTIFICATE-----`` lines before and after.
   See the final part of the inspected certificate output
   `here <https://wiki.shibboleth.net/confluence/display/CONCEPT/SAMLKeysAndCertificates>`_
   for an example of how this should look.

   Instructions on determining the format of a certificate using ``openssl``
   `can be found here <https://support.ssl.com/Knowledgebase/Article/View/19/0/der-vs-crt-vs-cer-vs-pem-certificates-and-how-to-convert-them>`_.

2. After the authority itself has been created, you will need to add an entity
   to represent the NYU SSO IdP. Click on ``Add saml2 entity defined by metadata providing url``
   in the top right corner of the ``Contents`` tab of the Authority object.
   You will need to provide an ID and a URL.  They should be the same value,
   the URL of the NYU SSO IdP. You need not provide a title, though it might
   make the ZMI more readable if you do.


`Step 3: Setup your SP <https://github.com/collective/collective.saml2#step-3-setup-your-sp>`_
----------------------------------------------------------------------------------------------

Once you have completed the process of adding and activating your SP PAS
plugin (#5 of 6 steps in the instructions), you'll need to do a few more things
before the plugin setup is complete.

1. Click on ``Add Saml attribute consuming service``.

This item is responsible for requesting specific attributes from the NYU SSO
IdP. By default, NYU will send ``sn`` (first name), ``givenName`` (last name),
and ``eduPersonPrincipalName``. However, this information will not be extracted
from the authentication response from NYU SSO unless they are represented in a
service. Set a descriptive title (?) for the new service object, and an ID. You
can leave the default values for ``index`` and ``language``. You may use the
description field to describe this object for the purpose of remembering what
it does, but remember that the description is included inline in the SP
Metadata sent to NYU SSO, so don't make it a novel.

2. While viewing the ``ACS (attribute consuming service)``, click
   ``Add Saml requested attribute`` to specify the attributes we need the
   service to send to us. For each attribute in the default set described
   above, use the following values:

+------------------------+----------------------------------+-------------+----------------+
| id                     | External attribute name          | Name format | Attribute type |
+========================+==================================+=============+================+
| sn                     | urn:oid:2.5.4.4                  | uri         | string         |
+------------------------+----------------------------------+-------------+----------------+
| givenName              | urn:oid:2.5.4.42                 | uri         | string         |
+------------------------+----------------------------------+-------------+----------------+
| eduPersonPrincipalName | urn:oid:1.3.6.1.4.1.5923.1.1.1.6 | uri         | string         |
+------------------------+----------------------------------+-------------+----------------+

**TODO:** As of this writing it is unclear how these attributes, once extracted
from the saml authentication response, are to be mapped to Plone user
attributes. Resolve this.

Required Updates
================

The default binding for the metadata provided by NYU's QA Shibboleth endpoint
is ``urn:mace:shibboleth:1.0:profiles:AuthnRequest``. However, this binding is
unsupported by ``dm.zope.saml2``.  In order to fix this problem we need to
manually set the binding when the ``Target`` object is instantiated in
``dm.zope.saml2.spsso.spsso`` on line 99. It must be set to
``urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST``.

We have to write this into the code ourselves, as there is no customization
point available for that aspect of things at this time. For that reason, we
will be using a fork of the package.

