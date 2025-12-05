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
    PRODUCTS = [
                'Maps',
                'Products.WebServerAuth',
                'WebServerAuth',
                'collective.easytemplate',
                'collective.easyslider',
                'collective.embedly',
                'collective.portlet.relateditems',
                'collective.quickupload',
                'isaw.bibitems',
                'wildcard.foldercontents',
                'Marshall',
                ]

    pqi = portal.portal_quickinstaller
    for PRODUCT in PRODUCTS:
        if pqi.isProductInstalled(PRODUCT):
            logger.info('uninstalling {}'.format(PRODUCT))
            pqi.uninstallProducts([PRODUCT])
    logger.info("All legacy products uninstalled ")


def toggleCachePurging(status='disabled'):
    from plone.cachepurging.interfaces import ICachePurgingSettings

    registry = getUtility(IRegistry)
    settings = registry.forInterface(ICachePurgingSettings, check=False)

    settings.enabled = False if status == 'disabled' else True

    transaction.commit()


def clean_registry_entries(portal):
    js_to_remove = ['++resource++plone.formwidget.geolocation/libs.js']
    css_to_remove = ['++resource++plone.formwidget.geolocation/libs.css',
                     '++resource++plone.formwidget.geolocation/maps.css',
                     'PressRoom.css']
    js_reg = portal.portal_javascripts
    css_reg = portal.portal_css
    for res in js_to_remove:
        if res in js_reg.getResourceIds():
            js_reg.manage_removeScript(id=res)
            logger.info("{} removed from {}".format(res, js_reg))
    for res in css_to_remove:
        if res in css_reg.getResourceIds():
            css_reg.manage_removeStylesheet(id=res)
            logger.info("{} removed from {}".format(res, css_reg))


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
    types = ('CV',
             'TemplatedDocument',

             'isaw.bibitems.bibitem',
             'isaw.policy.location',

             )
    for t in types:
        brains = pg(portal_type=t)
        for i, b in enumerate( brains):
            try:
                obj = b.getObject()
            except KeyError:
                logger.error("error deserializing {}".format(i))
                continue
            except AttributeError:
                logger.error("Object inexistent {} ... uncataloging".format(b.getPath()))
                pg.uncatalogObject(b.getPath())
                continue

            logger.info("{} removing: {}".format(b.portal_type, b.getPath()))
            api.content.delete(obj=obj,  check_linkintegrity=False)

    logger.info("Removing stale skin layers..")
    portal_types = portal.portal_types
    types_to_remove =(
        'PressClip',
        'PressContact',
        'PressRelease',
        'PressRoom')

    for t in types_to_remove:
        if t in portal_types.objectIds():
            portal_types.manage_delObjects([t])
            logger.info("Type '{}' removed from portal_types".format(t))


    logger.info("Removing nasty objects..")
    nasty_items = [
        '/isaw/research/io-figures/objects/snowman/',
    ]
    for item_path in nasty_items:
        obj = api.content.get(path=item_path)
        if obj is not None:
            api.content.delete(obj)
            logger.info('{} removed'.format(item_path))


def stale_skin_removal(portal):

    portal_skins = portal.portal_skins

    views_to_remove = [
    'pressroom_content',
    'pressroom_images',
    'pressroom_scripts',
    'pressroom_styles',
    ]

    for skin_name in portal_skins.getSkinSelections():
        path = portal_skins.getSkinPath(skin_name)
        path_list = [p.strip() for p in path.split(',')]


        new_path_list = [p for p in path_list if p not in views_to_remove]

        if new_path_list != path_list:
            portal_skins.addSkinSelection(skin_name, ','.join(new_path_list))
            logger.info("Skin '{}' updated: {}".format(skin_name, new_path_list))

    directory_views = portal_skins.objectIds()


    dv_to_remove = [
        'pressroom_content',
        'pressroom_content_2.5',
        'pressroom_images',
        'pressroom_scripts',
        'pressroom_styles',]

    # Elimina tutte le directory view
    for dv in dv_to_remove:
        if dv in directory_views:
            portal_skins.manage_delObjects([dv])
            logger.info("Removed Directory View: {}".format(dv))

def clean_catalog(portal):
    catalog = portal.portal_catalog
    columns_to_remove = ['image']
    schema = list(catalog.schema())
    logger.info("remove columns from catalog")

    for column in columns_to_remove:
        if column in schema:
            catalog.delColumn(column)
            logger.info('{} column removed'.format(column))


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


def clean_easyslider_addon(context):

    registry = portal.portal_registry
    to_delete = [k for k in registry.records.keys() if 'easyslider' in k.lower()]

    if not to_delete:
        print("No easyslider registry records found.")
    else:
        for key in to_delete:
            del registry.records[key]
            print("Deleted registry key:", key)

    # Remove control panel action
    cp = portal.portal_controlpanel

    actions = list(cp.listActions())
    found = False

    for index, action in enumerate(actions):
        _id = "easyslieder"  #SIC
        if action.id == _id :
            print("Deleting control panel action:", action.id, "-", action.title)
            cp.deleteActions([index])
            found = True
            break

    if not found:
        print("No easyslieder-related control panel action found.")


if __name__ == "__main__":


    unlockDavLocks()
    toggleCachePurging(status='disabled')

    stale_skin_removal(portal)
    remove_legacy_items(portal)
    clean_old_behaviors(portal)

    uninstall_lecacy_products(portal)

    toggleCachePurging(status='enabled')

    search_clean_portlets(portal, dryrun=False)

    clean_catalog(portal)

    clean_registry_entries(portal)
    clean_easyslider_addon(portal)

    transaction.commit()

    logger.info('end')
