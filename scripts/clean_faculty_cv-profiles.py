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


def unlockDavLocks():
    logger.info("Looking for DavLocked objects")
    davmanager = app.Control_Panel.get('DavLocks')
    locked_objs = davmanager.findLockedObjects(frompath='/')
    logger.info("found {} locked objects".format(len(locked_objs)))
    davmanager.unlockObjects(paths=[path for path, info in locked_objs])
    logger.info("...unlocked")
    transaction.commit()


def uninstall_faculty_stuff(portal):
    PRODUCT = 'isaw.facultycv'
    pqi = portal.portal_quickinstaller
    if pqi.isProductInstalled(PRODUCT):
        pqi.uninstallProducts([PRODUCT])


def toggleCachePurging(status='disabled'):
    from plone.cachepurging.interfaces import ICachePurgingSettings

    registry = getUtility(IRegistry)
    settings = registry.forInterface(ICachePurgingSettings, check=False)

    settings.enabled = False if status == 'disabled' else True

    transaction.commit()


def install_postmigration_products(portal):
    to_be_installed = []
    pqi = portal.portal_quickinstaller

    for prod in to_be_installed:
        if not pqi.isProductInstalled(prod):
            pqi.installProduct(prod)


def remove_cv_profiles(portal):
    pg = portal.portal_catalog
    types = ('CV', 'profile')
    for t in types:
        brains = pg(portal_type=t)
        for i, b in enumerate( brains):
            try:
                obj = b.getObject()
            except KeyError:
                logger.error("error deserializing {}".format(i))
                continue
            api.content.delete(obj=obj,  check_linkintegrity=False)


if __name__ == "__main__":

    unlockDavLocks()
    toggleCachePurging(status='disabled')

    remove_cv_profiles(portal)

    uninstall_faculty_stuff(portal)
    toggleCachePurging(status='enabled')

    transaction.commit()

    logger.info('end')