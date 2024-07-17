from AccessControl.SecurityManagement import newSecurityManager
from plone import api
from plone.app.contenttypes.migration import field_migrators
from plone.app.contenttypes.migration import migration
from plone.app.contenttypes.migration import topics
from plone.app.contenttypes.migration.field_migrators import FIELDS_MAPPING
from plone.app.contenttypes.migration.migration import migrateCustomAT
from transaction import commit
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.component.hooks import setSite
from zope.component.hooks import setSite
from zope.intid.interfaces import IIntIds
import logging
import transaction
from plone.dexterity.interfaces import IDexterityFTI


portal = app.Plone

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
    from plone.registry.interfaces import IRegistry
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

def migrate_default_types():
    catalog = portal.portal_catalog
    patch_ATEvent()

    (link_integrity,
     queue_indexing,
     patch_searchabletext) = migration.patch_before_migration(patch_searchabletext=True)

    migration.migrate_blobfiles(portal)
    migration.migrate_blobimages(portal)
    migration.migrate_documents(portal)
    migration.migrate_collections(portal)
    migration.migrate_events(portal)
    migration.migrate_links(portal)
    topics.migrate_topics(portal)

    catalog.clearFindAndRebuild()
    transaction.commit()
    # we must commit and reindex before migrating folders (God knows why)
    # otherwise bad things will happens

    migration.migrate_folders(portal)
    transaction.commit()

    catalog.clearFindAndRebuild()

    commit()

    unpatch_ATEvent()


same_name_fields = [
    ('image','NamedBlobImage'),
    ('imageCaption',  None),
    ]


def enable_ILeadeImageBehavior():
    types_to_enable = ['Page', 'Event', 'Folder']
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
    pass

def update_registry():
    default_profile = 'SOME PROFILE'
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile(default_profile, 'plone.app.registry')


if __name__ == "__main__":
    install_dexterity(portal)
    enable_ILeadeImageBehavior()
    uninstall_collectiveleadImage()

    # update_registry()
    migrate_default_types()
    logger.info('End migration default content type')