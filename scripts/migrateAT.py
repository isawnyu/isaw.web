from AccessControl.SecurityManagement import newSecurityManager
from plone import api
from plone.app.contenttypes.migration import migration
from plone.app.contenttypes.migration import topics
from plone.app.contenttypes.migration.utils import restore_references
from plone.app.contenttypes.migration.utils import store_references
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component.hooks import setSite
from plone.app.contenttypes.migration.migration import EventMigrator
from plone.app.contenttypes.migration.migration import migrate


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


def fix_registry(context=None):
    """Remove registry-records where the interface is no longer there."""
    registry = getUtility(IRegistry)
    keys = [i for i in registry.records.keys()]
    for key in keys:
        record = registry.records[key]
        if not record.field.interface:
            # That's fine...
            continue
        try:
            iface = record.field.interface()
        except TypeError:
            # That's also fine...
            continue
        if 'broken' in str(iface):
            logger.info('Removing broken record {key}'.format(key=key))
            del registry.records[key]


def patch_ATEvent():
    from Products.ATContentTypes.content.event import ATEvent
    from Products.ATContentTypes.content.event import IATEvent
    from DateTime import DateTime

    logger.info('Patching ATEvent to tollerate offset between timezoneless dates')
    old_cmp = ATEvent.__cmp__
    ATEvent.old_cmp = old_cmp

    def __cmp__(self, other):
        """Compare method

        If other is based on ATEvent, compare start, duration and title.
        #If other is a number, compare duration and number
        If other is a DateTime instance, compare start date with date
        In all other cases there is no specific order
        """
        # Please note that we can not use self.Title() here: the generated
        # edit accessor uses getToolByName, which ends up in
        # five.localsitemanager looking for a parent using a comparison
        # on this object -> infinite recursion.
        if IATEvent.providedBy(other):
            try:
                return cmp((self.start_date, self.duration, self.title),
                       (other.start_date, other.duration, other.title))
            except TypeError:
                # removing timezones for cmp
                logger.warning('notimezone in {}'.format(self))
                return cmp((self.start_date.replace(tzinfo=None), self.duration, self.title),
                        (other.start_date.replace(tzinfo=None), other.duration, other.title))

        elif isinstance(other, DateTime):
            return cmp(self.start(), other)
        else:
            # TODO come up with a nice cmp for types
            return cmp(self.title, other)

    ATEvent.__cmp__ = __cmp__

def unpatch_ATEvent():
    logger.info('unpatching ATEvent')
    from Products.ATContentTypes.content.event import ATEvent
    ATEvent.__cmp__ = ATEvent.old_cmp
    del ATEvent.old_cmp



def install_dexterity(portal):
    pqi = portal.portal_quickinstaller

    # replace default plone types with dexterity ones
    if not pqi.isProductInstalled('plone.app.dexterity'):
        pqi.installProduct('plone.app.dexterity')
    if not pqi.isProductInstalled('plone.app.contenttypes'):
        pqi.installProduct('plone.app.contenttypes')

    transaction.commit()


def migrate_folders(portal):

    weirdeness = [
        '/isaw/research/io-figures/images/',
        '/isaw/research/io-figures/objects/'
    ]

    folders = [
      '/isaw/about',
      '/isaw/academics',
      '/isaw/etaw/',
      '/isaw/events/',
      '/isaw/exhibitions/',
      '/isaw/graduate-studies/',
      '/isaw/guide/',
      '/isaw/help/',
      '/isaw/home-slides/',
      '/isaw/images/',
      '/isaw/jobs/',
      '/isaw/library/',
      '/isaw/members/',
      '/isaw/modify/',
      '/isaw/news/',
      '/isaw/people/',
      '/isaw/publications',
      '/isaw/rsvp',
      '/isaw/skunkworks',
      '/isaw/support-isaw',
      '/isaw/visiting-scholars',
      '/isaw/research/io-figures/images/',
      '/isaw/research',
    ]


    for w in weirdeness:
        logger.info("migrating weirdness {}".format(w))
        w = portal.unrestrictedTraverse(w)
        migrate_wierdness(w)
        transaction.commit()

    for f in folders:
        logger.info("migrating {}".format(f))
        f = portal.unrestrictedTraverse(f)
        migration.migrate_folders(f)
        transaction.commit()


def migrate_wierdness(folder):
    # create a backup like container
    if folder.meta_type != 'ATFolder':
        return

    parent = folder.aq_parent
    folder_id = folder.getId()
    bak_dir_id = folder.getId() + "_bak"
    bak_dir = api.content.create(container=parent,
                       type='Folder',
                       id=bak_dir_id,
                       title="TEMP for {}".format(bak_dir_id))

    #move all folder contents to back dir
    for obj in folder.objectValues():
        api.content.move(source=obj, target=bak_dir)

    # migrate folder
    migration.migrate_folders(folder)
    folder =  getattr(parent, folder_id)

    # move back contents into new DX Folder
    for obj in bak_dir.objectValues():
        api.content.move(source=obj, target=folder)

    # delete backup dir
    api.content.delete(obj=bak_dir)


from plone.app.contenttypes.migration.migration import migrate_simplefield
from plone.app.contenttypes.migration.migration import migrate_datetimefield
from plone.app.contenttypes.migration.migration import migrate_richtextfield

class ISAWEventMigrator(EventMigrator):
    """Migrate both Products.ContentTypes & plone.app.event.at Events"""

    def migrate_schema_fields(self):
        migrate_datetimefield(self.old, self.new, 'startDate', 'start')
        migrate_datetimefield(self.old, self.new, 'endDate', 'end')

        migrate_richtextfield(self.old, self.new, 'text', 'text')
        migrate_simplefield(self.old, self.new, 'location', 'location')
        migrate_simplefield(self.old, self.new, 'attendees', 'attendees')
        migrate_simplefield(self.old, self.new, 'eventUrl', 'event_url')
        migrate_simplefield(self.old, self.new, 'contactName', 'contact_name')
        migrate_simplefield(
            self.old, self.new, 'contactEmail', 'contact_email')
        migrate_simplefield(
            self.old, self.new, 'contactPhone', 'contact_phone')
        migrate_simplefield(self.old, self.new, 'wholeDay', 'whole_day')
        migrate_simplefield(self.old, self.new, 'openEnd', 'open_end')
        migrate_simplefield(self.old, self.new, 'recurrence', 'recurrence')

        # custom ATSchemaExtendendFields
        migrate_simplefield(self.old, self.new, 'subtitle', 'subtitle')
        migrate_simplefield(self.old, self.new, 'eventType', 'eventType')
        migrate_simplefield(self.old, self.new, 'speaker', 'speaker')
        migrate_simplefield(self.old, self.new, 'speakerAffiliation', 'speakerAffiliation')
        migrate_simplefield(self.old, self.new, 'rsvpRequired', 'rsvpRequired')


def unlockDavLocks():
    logger.info("Looking for DavLocked objects")
    davmanager = app.Control_Panel.get('DavLocks')
    locked_objs = davmanager.findLockedObjects(frompath='/isaw')
    logger.info("found {} locked objects".format(len(locked_objs)))
    davmanager.unlockObjects(paths=[path for path, info in locked_objs])
    logger.info("...unlocked")
    transaction.commit()

def migrate_default_types():
    patch_ATEvent()
#    unlockDavLocks()
    store_references(portal)

    migration.migrate_blobfiles(portal)
    migration.migrate_blobimages(portal)

    migration.migrate_documents(portal)
    migration.migrate_collections(portal)

    migrate(portal, ISAWEventMigrator)

    migration.migrate_links(portal)
    topics.migrate_topics(portal)
    migration.migrate_newsitems(portal)

    # we must commit and reindex before migrating folders (God knows why)
    # otherwise bad things will happens
    logger.info('Starting a catalog reindex...')
    #portal.portal_catalog.clearFindAndRebuild()
    transaction.commit()

    migrate_folders(portal)
    transaction.commit()

    # some members folder did not get migrated in the first run
    # so we rerun the migration folders (only those still AT will go through the process)
    migrate_folders(portal)


    unpatch_ATEvent()
    restore_references(portal)
    logger.info("End migration default ATCT to Dexterity")


same_name_fields = [
    ('image','NamedBlobImage'),
    ('imageCaption',  None),
    ]


def enable_ILeadeImageBehavior():
    types_to_enable = ['Document', 'Event', 'Folder', 'File', 'Collection', 'Topic']
    behavior = "plone.app.contenttypes.behaviors.leadimage.ILeadImage"
    pt_tool = portal.portal_types
    for _type in types_to_enable:
        p_type = pt_tool.get(_type)

        if IDexterityFTI.providedBy(p_type):
            behaviors_list = list(p_type.getProperty('behaviors'))

            if behavior in behaviors_list and behaviors_list.index(behavior) != 0:
                behaviors_list.remove(behavior)

            if behavior not in behaviors_list:
                behaviors_list.insert(0, behavior)

            p_type._updateProperty('behaviors', tuple(behaviors_list))


def uninstall_collectiveleadImage():
    # XXX

    # remove OLD c.leadeimage adapter from portal
    # uninstall c.leadeimage
    PRODUCT = 'collective.contentleadimage'
    pqi = portal.portal_quickinstaller
    if pqi.isProductInstalled(PRODUCT):
        pqi.uninstallProducts([PRODUCT])


def toggleContentRules(status='disabled'):
    from plone.contentrules.engine.interfaces import IRuleStorage

    crules = getUtility(IRuleStorage)
    crules.active = False if status == 'disabled' else True
    transaction.commit()

def toggleLinkIntegrity(status='disabled'):
    site_properties = portal.portal_properties.site_properties
    value = False if status == 'disabled' else True
    props = {'enable_link_integrity_checks': value}

    site_properties.manage_changeProperties(**props)

    transaction.commit()

def toggleCachePurging(status='disabled'):
    from plone.cachepurging.interfaces import ICachePurgingSettings

    registry = getUtility(IRegistry)
    settings = registry.forInterface(ICachePurgingSettings, check=False)

    settings.enabled = False if status == 'disabled' else True

    transaction.commit()


def patch_transform():
    from plone.app.textfield.transform import PortalTransformsTransformer
    from plone.app.textfield.transform import getSite
    from plone.app.textfield.transform import getToolByName
    from plone.app.textfield.transform import TransformError
    from plone.app.textfield.transform import LOG
    from plone.app.textfield.transform import ConflictError

    PortalTransformsTransformer.old__call__ = PortalTransformsTransformer.__call__

    def new_call(self, value, mimeType):
        # shortcut it we have no data
        if value.raw is None:
            return u''

        # shortcut if we already have the right value
        if mimeType is value.mimeType:
            return value.output

        site = getSite()

        transforms = getToolByName(site, 'portal_transforms', None)
        if transforms is None:
            raise TransformError("Cannot find portal_transforms tool")

        try:
            data = transforms.convertTo(mimeType,
                                        value.raw_encoded,
                                        mimetype=value.mimeType,
                                        context=self.context,
                                        # portal_transforms caches on this
                                        object=value._raw_holder,
                                        encoding=value.encoding)
            if data is None:
                # TODO: i18n
                msg = (u'No transform path found from "%s" to "%s".' %
                       (value.mimeType, mimeType))
                LOG.error(msg)
                # TODO: memoize?
                # plone_utils = getToolByName(self.context, 'plone_utils')
                # plone_utils.addPortalMessage(msg, type='error')
                # FIXME: message not always rendered, or rendered later on
                # other page.
                # The following might work better, but how to get the request?
                # IStatusMessage(request).add(msg, type='error')
                return u''

            else:
                output = data.getData()
                return output.decode(value.encoding)
        except ConflictError:
            raise
        except Exception as e:
            # log the traceback of the original exception
            LOG.error("Transform exception", exc_info=True)

            #raise TransformError('Error during transformation', e)

        logger.info("### PATCH plone.app.textfield.transform... swallow any transform error during migration")

        PortalTransformsTransformer.__call__ = new_call

if __name__ == "__main__":
    install_dexterity(portal)
    enable_ILeadeImageBehavior()

    toggleCachePurging(status='disabled')
    toggleContentRules(status='disabled')
    toggleLinkIntegrity(status='disabled')

    patch_transform()

    migrate_default_types()

    toggleContentRules(status='enabled')
    toggleCachePurging(status='enabled')
    toggleLinkIntegrity(status='enabled')

    uninstall_collectiveleadImage()

    transaction.commit()

    logger.info('End migration default content types')