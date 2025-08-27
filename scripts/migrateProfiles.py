from AccessControl.SecurityManagement import newSecurityManager

from plone import api
from plone.app.contenttypes.migration.migration import ATCTFolderMigrator, migrate
from plone.app.contenttypes.migration.field_migrators import (
    migrate_simplefield, migrate_richtextfield, migrate_imagefield
)

from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component.hooks import setSite
from zope.lifecycleevent import modified
import logging
import transaction


portal = app.isaw

logging.getLogger().setLevel(logging.INFO)
for handler in logging.getLogger().handlers:
    handler.setLevel(logging.INFO)

logger = logging.getLogger("isaw.web.scripts.migrateProfiles")

user_name_or_id = "admin"
user = app.acl_users.getUser(user_name_or_id)
newSecurityManager(None, user.__of__(app.acl_users))

setSite(portal)


def disable_resolve_uid_captioning_adapter(portal):
    from zope.component import getGlobalSiteManager
    from plone.outputfilters.interfaces import IFilter

    gsm = getGlobalSiteManager()
    gsm.unregisterAdapter(
        required=(None, None), provided=IFilter, name="resolveuid_and_caption"
    )


def toggleContentRules(status="disabled"):
    from plone.contentrules.engine.interfaces import IRuleStorage

    crules = getUtility(IRuleStorage)
    crules.active = False if status == "disabled" else True
    transaction.commit()


def toggleLinkIntegrity(status="disabled"):
    site_properties = portal.portal_properties.site_properties
    value = False if status == "disabled" else True
    props = {"enable_link_integrity_checks": value}

    site_properties.manage_changeProperties(**props)

    transaction.commit()


def toggleCachePurging(status="disabled"):
    from plone.cachepurging.interfaces import ICachePurgingSettings

    registry = getUtility(IRegistry)
    settings = registry.forInterface(ICachePurgingSettings, check=False)

    settings.enabled = False if status == "disabled" else True

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
            return ""

        # shortcut if we already have the right value
        if mimeType is value.mimeType:
            return value.output

        site = getSite()

        transforms = getToolByName(site, "portal_transforms", None)
        if transforms is None:
            raise TransformError("Cannot find portal_transforms tool")

        try:
            data = transforms.convertTo(
                mimeType,
                value.raw_encoded,
                mimetype=value.mimeType,
                context=self.context,
                # portal_transforms caches on this
                object=value._raw_holder,
                encoding=value.encoding,
            )
            if data is None:
                # TODO: i18n
                msg = 'No transform path found from "%s" to "%s".' % (
                    value.mimeType,
                    mimeType,
                )
                LOG.error(msg)
                # TODO: memoize?
                # plone_utils = getToolByName(self.context, 'plone_utils')
                # plone_utils.addPortalMessage(msg, type='error')
                # FIXME: message not always rendered, or rendered later on
                # other page.
                # The following might work better, but how to get the request?
                # IStatusMessage(request).add(msg, type='error')
                return ""

            else:
                output = data.getData()
                return output.decode(value.encoding)
        except ConflictError:
            raise
        except Exception as e:
            # log the traceback of the original exception
            LOG.error("Transform exception", exc_info=True)

            # raise TransformError('Error during transformation', e)

    logger.info(
        "### PATCH plone.app.textfield.transform... swallow any transform error during migration"
    )
    PortalTransformsTransformer.__call__ = new_call


def delete_cvs():
    """
    Delete all CVs in the portal.
    """
    count = 0
    catalog = api.portal.get_tool("portal_catalog")
    for brain in list(catalog.unrestrictedSearchResults(portal_type="CV")):
        obj = brain.getObject()
        api.content.delete(obj=obj)
        count += 1
    transaction.commit()
    logger.info("Deleted %s CVs" % count)


def upgrade_packages():
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.upgradeProfile("isaw.facultycv:default")
    portal_setup.upgradeProfile("isaw.policy:default")


class ProfileMigrator(ATCTFolderMigrator):
    """Migrator for Profile content type"""

    src_portal_type = "profile"
    src_meta_type = "Profile"
    dst_portal_type = "Profile"
    dst_meta_type = None

    def migrate_schema_fields(self):
        migrate_imagefield(self.old, self.new, 'Image', 'profileImage')
        migrate_richtextfield(self.old, self.new, 'Titles', 'titles')
        migrate_simplefield(self.old, self.new, 'pronouns', 'pronouns')
        migrate_simplefield(self.old, self.new, 'Phone', 'phone')
        migrate_simplefield(self.old, self.new, 'Email', 'email')
        migrate_simplefield(self.old, self.new, 'Address', 'address')
        migrate_richtextfield(self.old, self.new, 'Profile Blurb', 'profileBlurb')
        migrate_simplefield(self.old, self.new, 'ExternalURIs', 'external_links')
        migrate_simplefield(self.old, self.new, 'MemberID', 'user_id')
        migrate_simplefield(self.old, self.new, 'NamedLocation', 'named_location')

    def migrate_at_uuid(self):
        super(ProfileMigrator, self).migrate_at_uuid()
        self.old.reindexObject(idxs=['UID'])

    def migrate(self, unittest=0):
        super(ProfileMigrator, self).migrate(unittest)
        # make sure it gets reindexed
        modified(self.new)


def migrate_profiles():
    portal = api.portal.get()

    migrate(portal, ProfileMigrator)

    redirection_types = portal.portal_redirection.getRedirectionAllowedForTypes()
    if "Profile" not in redirection_types:
        redirection_types.append("Profile")
        portal.portal_redirection.setRedirectionAllowedForTypes(redirection_types)


if __name__ == "__main__":

    toggleCachePurging(status="disabled")
    toggleContentRules(status="disabled")
    toggleLinkIntegrity(status="disabled")
    disable_resolve_uid_captioning_adapter(portal)
    patch_transform()

    # remove bad catalog entries:
    # - /isaw/people/faculty/isaw-faculty/alexander-jones/PMath_cover_thumb.jpeg
    delete_cvs()
    upgrade_packages()
    migrate_profiles()

    toggleContentRules(status="enabled")
    toggleCachePurging(status="enabled")
    toggleLinkIntegrity(status="enabled")

    transaction.commit()
    logger.info("End migration of profile content type")
