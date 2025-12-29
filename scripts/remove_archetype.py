from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.interfaces import IMetadataTool
from Testing import makerequest
from plone import api
from plone.app.upgrade.utils import loadMigrationProfile
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import setSite
from zope.interface import noLongerProvides
import logging
import sys
import transaction

logging.getLogger().setLevel(logging.INFO)

for handler in logging.getLogger().handlers:
    handler.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

user_name_or_id = 'admin'
user = app.acl_users.getUser(user_name_or_id)
newSecurityManager(None, user.__of__(app.acl_users))

root = makerequest.makerequest(app)

site = app.isaw
setSite(site)


def unlockDavLocks():
    logger.info("Looking for DavLocked objects")
    davmanager = app.Control_Panel.DavLocks
    locked_objs = davmanager.findLockedObjects(frompath='/')
    logger.info("found {} locked objects".format(len(locked_objs)))
    davmanager.unlockObjects(paths=[path for path, info in locked_objs])
    logger.info("...unlocked")
    ##transaction.commit()

def toggleCachePurging(status='disabled'):
    from plone.cachepurging.interfaces import ICachePurgingSettings

    registry = getUtility(IRegistry)
    settings = registry.forInterface(ICachePurgingSettings, check=False)

    settings.enabled = False if status == 'disabled' else True

    #transaction.commit()

def fulvio_cleans(portal):
    # remove obsolete AT tools
    tools = [
        'portal_languages',
        'portal_tinymce',
        'kupu_library_tool',
        'portal_factory',
        'portal_atct',
        'uid_catalog',
        'archetype_tool',
        'reference_catalog',
        'portal_metadata',
    ]
    for tool in tools:
        try:
            portal.manage_delObjects([tool])
            logger.warning('Deleted {}'.format(tool))
        except AttributeError:
            logger.warning('{} not found'.format(tool))

    sm = portal.getSiteManager()
    try:
        sm.getUtility(provided=IMetadataTool)
        sm.unregisterUtility(provided=IMetadataTool)
        print("Found IMetadataTool. unregistered")
    except ComponentLookupError:
        pass
    print("Removed Archetypes leftovers")

    # reapply uninstall to get rid of IATCTTool component
    try:
        loadMigrationProfile(
            portal,
            'profile-Products.ATContentTypes:uninstall',
        )
    except KeyError:
        pass
    ##transaction.commit()

def clean_products(site):
    pqi = api.portal.getToolByName(site, 'portal_quickinstaller')

    uninstallingProducts = ['Products.Archetypes',
                            'ATExtensions',
                            'ATContentTypes',
                            'Archetypes',
                            'plone.app.referenceablebehavior',
                            'archetypes.referencebrowserwidget',
                            'plone.app.collection',
                            ]
    for unprod in uninstallingProducts:
        print('Uninstalling: {}...'.format(unprod))
        if pqi.isProductInstalled(unprod):
            pqi.uninstallProducts([unprod])
            print('...uninstalled')
    transaction.commit()

def remove_behaviors_from_portal_types(site, interfaces=[]):
    """ browsing portal_type removing unwanted behaviors
    """

    identifiers = [i.__identifier__ for i in interfaces]
    ptypes = site.portal_types
    for id, ptype  in ptypes.objectItems():
        if ptype.hasProperty('behaviors'):
            newprop = [iface for iface in ptype.getProperty('behaviors')
            if iface  not in identifiers]

            if set(newprop) != set(ptype.getProperty('behaviors')):
                ptype.manage_changeProperties(behaviors=newprop)
                print('cleaned {} from unwanted behaviors {}'.format(id, interfaces))


def clear_cmfeditions(site):
    site.portal_historiesstorage._shadowStorage._storage.clear()
    site.portal_historiesstorage.zvc_repo._histories.clear()


def clean_broken_relations(site):
    from zc.relation.interfaces import ICatalog
    catalog = getUtility(ICatalog)
    broken = [rel for rel in catalog if rel.to_id is None or rel.from_object is None]
    print("Removing {} broken relations...".format(len(broken)))
    for rel in broken:
        catalog.unindex(rel)


def rebuild_intids(site):
    from zc.relation.interfaces import ICatalog
    from zope.intid.interfaces import IIntIds
    from zope.keyreference.interfaces import IKeyReference

    print("Rebuilding intids...")
    intids = getUtility(IIntIds)
    old_ids = intids.ids
    old_refs = intids.refs
    print("Before: {} entries".format(len(old_ids)))
    intids.ids = intids.family.OI.BTree()
    intids.refs = intids.family.IO.BTree()

    # restore content intids
    i = 0
    for brain in site.portal_catalog.unrestrictedSearchResults(path="/"):
        obj = brain._unrestrictedGetObject()
        key = IKeyReference(obj)
        uid = old_ids.get(key)
        if uid is None:
            continue
        intids.ids[key] = uid
        intids.refs[uid] = key
        i += 1
        if not i % 100:
            print(i)

    # restore relation intids
    catalog = getUtility(ICatalog)
    for uid in catalog._relTokens:
        key = old_refs[uid]
        intids.ids[key] = uid
        intids.refs[uid] = key
        i += 1
        if not i % 100:
            print(i)

    print("After: {} entries".format(len(intids.ids)))


if __name__ == "__main__":

    unlockDavLocks()
    toggleCachePurging(status='disabled')

    fulvio_cleans(site)
    clean_products(site)

    # import ipdb;ipdb.set_trace()

    transaction.commit()

    clear_cmfeditions(site)
    clean_broken_relations(site)
    rebuild_intids(site)

    #toggleCachePurging(status='enabled')

    logger.info('end remove and archetypes')

transaction.commit()
