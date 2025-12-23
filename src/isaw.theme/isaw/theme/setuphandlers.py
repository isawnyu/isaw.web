from .browser.interfaces import IISAWSettings
from Products.CMFCore.utils import getToolByName
from isaw.theme.browser.interfaces import IISAWSettings
from logging import getLogger
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import six
from zope.component import getMultiAdapter

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

def fix_events_calendar_portlet_configuration(context):
    portal = api.portal.get()
    from plone.app.event.portlets.portlet_calendar import ICalendarPortlet
    from plone.portlets.interfaces import IPortletAssignmentMapping
    from plone.portlets.interfaces import IPortletManager
    state =  ('external', 'internally_published', 'published')

    # found so far
    paths_to_fix = ['/isaw/events/event-home',
    '/isaw/events/community-standards-policy',
    '/isaw/events/video-archive',
    '/isaw/events/scribal-mind',
    ]

    def fix_for(context, assignment):
        logger.info("fix_events_calendar_portlet_configuration in {}".format(context.getId()))
        if not assignment.state:
            assignment.state = state
            logger.info("{} state...fixed".format(context))

        if not isinstance(assignment.search_base_uid, unicode):
            assignment.search_base_uid = unicode(context.aq_parent.UID())
            logger.info("{} search_base...fixed".format(context))


    def _clean(context,  _interface , dryrun=True, reset=False):
        for manager_name in ["plone.leftcolumn", "plone.rightcolumn"]:
            manager = getUtility(
                IPortletManager, name=manager_name, context=context)
            mapping = getMultiAdapter(
                (context, manager), IPortletAssignmentMapping)
            for id, assignment in mapping.items():
                if _interface.providedBy(assignment):
                    fix_for(context, assignment)


    pg = portal.portal_catalog
    brains = pg.unrestrictedSearchResults()

    total = float(len(brains))
    for i, b in enumerate(brains):
        if i > 0 and not i % 500:
            logger.info('...{:.2f}% completed' .format(i/total*100.0))
        obj = b.getObject()
        _clean(obj, ICalendarPortlet)

    logger.info('\n\n=== finish portlet calendar fix. Found {} portlets '.format(
        total))




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

    # disable portal tabs other than folderish
    api.portal.set_registry_record('plone.nonfolderish_tabs', value=False)

    fix_events_calendar_portlet_configuration(context)