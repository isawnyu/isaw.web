from .browser.interfaces import IISAWSettings
from Products.CMFCore.utils import getToolByName
from isaw.theme.browser.interfaces import IISAWSettings
from logging import getLogger
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import six

logger = getLogger(__name__)

#from sixfeetup.utils import helpers as sfutils


PROFILE_ID = 'profile-isaw.theme:default'

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('isaw.theme_default.txt') is None:
        return

    # Add additional setup code here
    # automagically run a plone migration if needed
    #sfutils.runPortalMigration()
    # automagically run the upgrade steps for this package
    #sfutils.runUpgradeSteps(u'isaw.theme:default')

def set_property(context, prop_name, value):
   if context.hasProperty(prop_name):
       context.manage_changeProperties(prop_name=value)
   else:
       context.manage_addProperty(prop_name, value, 'string')

def set_layout(context, layout_name):
    if context.hasProperty('default_page'):
        context.manage_delProperties(['default_page'])
    set_property(context, 'layout', layout_name)

def set_default_page(context, page_id):
    if context.hasProperty('layout'):
        context.manage_delProperties(['layout'])
    set_property(context, 'default_page', page_id)

def publish(context):
    portal_workflow = getToolByName(context, 'portal_workflow')
    portal_workflow.doActionFor(
        context,
        'publish',
        comment='Content published automatically'
    )

def createHomePage(context):
    site = context.getParentNode()
    page_id = 'isaw'
    if page_id not in site.objectIds():
        site.invokeFactory('Document', page_id)
        home_page = site[page_id]
        title = 'Institute for the Study of the Ancient World'
        home_page.processForm(values={'title': title})
        set_layout(home_page, 'home_page_view')
        publish(home_page)
        set_default_page(site, page_id)

def set_calendar_types(context):
    ct = getToolByName(context, 'portal_calendar')
    ct.edit_configuration(show_types=('Event',),
        use_session=False,
        show_states=('published', 'external', 'internally_published'),
        firstweekday=6)


def add_footer_registry_keys(context):
    """Upgrade step: add footer settings keys to registry."""

    registry = getUtility(IRegistry)

    # Ensure the interface is registered
    try:
        registry.forInterface(IISAWSettings)
    except KeyError:
        registry.registerInterface(IISAWSettings)

    # Set default values if not already present
    defaults = {
        'column_one': u'',
        'column_two': u'',
        'disclaimer': u'',
    }

    settings = registry.forInterface(IISAWSettings)
    for key, value in defaults.items():
        if not getattr(settings, key, None):
            setattr(settings, key, value)

def to_plone_51(context):
    """ include steps to complete plone51 migration

     - import resource registry
    """
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile(
         PROFILE_ID, 'plone.app.registry', run_dependencies=False
     )
    logger.info('registry updated')

    # convert registry isawsettings into RichValue

    registry = getUtility(IRegistry)
    settings = registry.forInterface(IISAWSettings, False)
    fields = [
              'column_one',
              'column_two',
              'disclaimer',
              'emergency_message',
              'footer_html',
              'no_results_message',
    ]
    for key in fields:
        value = getattr(settings, key, u'')
        if isinstance(value, six.string_types):
            value = RichTextValue(
                raw=value,
                mimeType='text/html',
                outputMimeType='text/x-html-safe',
            )
            setattr(settings, key, value)
            logger.info('converted {} in RichTextValue'.format(key))
