import os
from os import environ
from StringIO import StringIO
import logging
import urllib2

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Testing.makerequest import makerequest
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy, OmnipotentUser

# Force application logging level to DEBUG and log output to stdout for all loggers
import sys, logging

HOSTNAME = 'isaw4.atlantides.org'
HOSTPORT = '8083'
app.isaw

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root_logger.addHandler(handler)

def spoofRequest(app):
    """
    Make REQUEST variable to be available on the Zope application server.

    This allows acquisition to work properly
    """
    _policy=PermissiveSecurityPolicy()
    _oldpolicy=setSecurityPolicy(_policy)
    newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))
    info = {'SERVER_NAME': 'isaw4.atlantides.org',
            'SERVER_PORT': '8083',
            'REQUEST_METHOD':  'GET'}
    return makerequest(app, environ=info)

# Enable Faux HTTP request object
app = spoofRequest(app)

# Get Plone site object from Zope application server root
site = app.unrestrictedTraverse("isaw")
REQUEST = site.setupCurrentSkin(app.REQUEST)

# Clean this up depending on how you plan to use it
# Basically use urllib or whatever etc etc
# Christopher Warner

print("<h2>ISAW site contents</h2>")
print("""
        <html>
        <style type="text/css">
        <!--
        td:hover{background-color:#E6CCAC;}
        td:hover{color:#A44A26;}
        -->
        </style>
        <table width=100%%>
        """)
for x in app.isaw.portal_catalog(path={'query': '/', 'depth': 10}):
    print("""
        <tr>
        <td width=10%%>%s</td>
        <td width=90%%><a href="%s">%s</a></td>
        </tr>
        <tr></tr>
        """ % (x["Title"], x.getURL(), x.getURL()))

print("""
        </table>
        </html>
        """)
