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


def uninstall_lecacy_products(portal):
    PRODUCTS = ['isaw.facultycv',
                'isaw.bibitems',
                'Maps',
                'collective.easytemplate',
                'collective.portlet.relateditems',
                'wildcard.foldercontents',
                'Products.WebServerAuth',
                'collective.quickupload',
                ]

    pqi = portal.portal_quickinstaller
    for PRODUCT in PRODUCTS:
        if pqi.isProductInstalled(PRODUCT):
            pqi.uninstallProducts([PRODUCT])


def toggleCachePurging(status='disabled'):
    from plone.cachepurging.interfaces import ICachePurgingSettings

    registry = getUtility(IRegistry)
    settings = registry.forInterface(ICachePurgingSettings, check=False)

    settings.enabled = False if status == 'disabled' else True

    transaction.commit()


def clean_old_behaviors(portal):
    bh_to_remove = ['isaw.policy.map_extender.IGeolocationBehavior',
                    'plone.app.stagingbehavior.interfaces.IStagingSupport']
    pt_tool = portal.portal_types

    for p_type in pt_tool.objectValues():
        if not IDexterityFTI.providedBy(p_type):
            continue

        behaviors_list = list(p_type.getProperty('behaviors', []))
        for bh in  bh_to_remove:
            if bh in behaviors_list:
                behaviors_list.remove(bh)
                logger.info('removed {} from {}'.format(bh, p_type))

        p_type._updateProperty('behaviors', tuple(behaviors_list))


def install_postmigration_products(portal):
    to_be_installed = []
    pqi = portal.portal_quickinstaller

    for prod in to_be_installed:
        if not pqi.isProductInstalled(prod):
            pqi.installProduct(prod)


def remove_legacy_items(portal):
    pg = portal.portal_catalog
    types = ('CV', 'profile', 'isaw.bibitems.bibitem')
    for t in types:
        brains = pg(portal_type=t)
        for i, b in enumerate( brains):
            try:
                obj = b.getObject()
            except KeyError:
                logger.error("error deserializing {}".format(i))
                continue
            api.content.delete(obj=obj,  check_linkintegrity=False)



def search_clean_portlets(portal, dryrun=True):
    from plone.portlets.interfaces import IPortletManager
    from plone.portlets.interfaces import IPortletAssignmentMapping

    found_log_template = """
     {path}
     manager: {manager}
     id: {id}
     uid/ref: {uid_ref}
     action: {action}
     ==================
    """
    def _clean(context,  portlet_interfaces, dryrun=True, reset=False):

        path = '/'.join(context.getPhysicalPath())
        found = 0
        for manager_name in ["plone.leftcolumn", "plone.rightcolumn"]:
            manager = getUtility(
                IPortletManager, name=manager_name, context=context)
            mapping = getMultiAdapter(
                (context, manager), IPortletAssignmentMapping)
            for id, assignment in mapping.items():
                for _interface in  portlet_interfaces:
                    if not _interface.providedBy(assignment):
                        continue

                    action = dryrun and 'Found' or 'Found and removed '
                    data = dict(action=action,
                                manager=manager_name,
                                id=id,
                                path=path,
                                uid_ref=context.__repr__(),
                                user=api.user.get_current().getId(),
                                )
                    logger.info(
                            found_log_template.format(**data))
                    found += 1
                    if not dryrun:
                        del(mapping[id])
        return found


    portlet_interfaces = []
    try:
        from collective.portlet.relateditems.relateditems import IRelatedItems
        portlet_interfaces.append(IRelatedItems)
    except:
        pass
    try:
        from collective.quickupload.portlet.quickuploadportlet import IQuickUploadPortlet
        portlet_interfaces.append(IQuickUploadPortlet)
    except:
        pass

    if not portlet_interfaces:
        logger.info("No portlet interfaces to remove found.")
        return 0

    pg = portal.portal_catalog
    brains = pg.unrestrictedSearchResults()

    total = float(len(brains))
    found = 0
    for i, b in enumerate(brains):
        if i > 0 and not i % 100:
            logger.info('...{:.2f}% completed' .format(i/total*100.0))
        obj = b.getObject()
        num_erased = _clean(obj, portlet_interfaces, dryrun=dryrun, )
        found +=num_erased

    logger.info('\n\n=== finish portlet cleaning. Found {} portlets '.format(
                total))


if __name__ == "__main__":

    unlockDavLocks()
    toggleCachePurging(status='disabled')

    remove_legacy_items(portal)
    clean_old_behaviors(portal)

    uninstall_lecacy_products(portal)
    toggleCachePurging(status='enabled')

    search_clean_portlets(portal, dryrun=False)

    transaction.commit()

    logger.info('end')
