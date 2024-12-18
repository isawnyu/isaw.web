from AccessControl.SecurityManagement import newSecurityManager
from json import dump
from json import load
from plone import api
from plone.app.contenttypes.migration import migration
from plone.app.contenttypes.migration import topics
from plone.app.contenttypes.migration.migration import DocumentMigrator
from plone.app.contenttypes.migration.migration import EventMigrator
from plone.app.contenttypes.migration.migration import migrate
from plone.app.contenttypes.migration.utils import link_items
from plone.app.contenttypes.migration.utils import restore_references
from plone.app.contenttypes.migration.utils import store_references
from plone.app.contenttypes.migration.utils import uuidToObject
from plone.app.event import browser
from plone.dexterity.interfaces import IDexterityFTI
from plone.event.utils import default_timezone
from plone.registry.interfaces import IRegistry
from z3c.relationfield import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import setSite
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds
import logging
import transaction


portal = app.isaw

logging.getLogger().setLevel(logging.INFO)
for handler in logging.getLogger().handlers:
    handler.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

user_name_or_id = 'admin'
user = app.acl_users.getUser(user_name_or_id)
newSecurityManager(None, user.__of__(app.acl_users))

setSite(portal)

NASTY = ('_ATContentTypes__',
         '_isaw_facultycv__',
         '_collective_easytemplate_',
         '_Add_')

def getObjects(portal):
    pg = portal.portal_catalog
    for b in pg.unrestrictedSearchResults(show_inactive=True):
        try:
            obj = b.getObject()
            yield obj
        except:
            logger.error("problem getting {}".format(b.getPath()))

def cleanObj(obj):
    for key in vars(obj).keys():
        for n in NASTY:
            if key.startswith(n):
                delattr(obj, key)

    logger.info("cleaned obj: {}".format(obj.absolute_url()))


logger.info("Cleaning {} attributes from Zodb objects".format(NASTY))

for obj in getObjects(portal):
    cleanObj(obj)

transaction.commit()

logger.info('done')

