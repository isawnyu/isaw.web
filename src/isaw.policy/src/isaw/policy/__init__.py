# Disable the HomeFolderLocator from plone.app.iterate
from . import patches
from plone.app.upgrade.utils import alias_module
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
import logging

# XXX: Why did we disable home folder finding?
# from plone.app.iterate.containers import HomeFolderLocator
# HomeFolderLocator.available = False


# Set up the i18n message factory for our package
MessageFactory = MessageFactory('isaw.policy')

logger = logging.getLogger('isaw.policy')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    patches.patch_saml_login()




from Persistence import Persistent

class LocalAssignmentUtility(Persistent):
    """dummy"""

class Registry(Persistent):
    """dummy"""

class Dummy(object):
    """dummy"""

    def __init__(self, id):
        self.id = id

    def getId(self):
        return "fake_id Dummy class"

    def getPortalTypeName(self, ):
        return "fake_portal_type Dummy class"

class DummyP(Dummy, Persistent):
    pass


# aliasing legacy modules/classes to please the storage
alias_module('Products.CMFDefault.DiscussionItem.DiscussionItemContainer', Dummy)
alias_module('Products.Maps.adapters.Geolocation', Dummy)
alias_module('Products.Marshall.registry.Registry', Registry)
alias_module('collective.embedly.interfaces.IEmbedlySettings', Interface)
alias_module('collective.quickupload.interfaces.IQuickUploadCapable', Interface)
alias_module('grokcore.component.interfaces.IContext', Interface)
alias_module('isaw.facultycv.content.cv.CV', Dummy)
alias_module('isaw.facultycv.content.profile.profile', Dummy)
alias_module('isaw.policy.map_extender.IGeolocationBehavior', Interface)
alias_module('isaw.policy.map_extender.ILocation', Interface)
alias_module('plone.app.event.interfaces.IEventSettings', Interface)
alias_module('plone.app.stagingbehavior.interfaces.IStagingSupport', Interface)
alias_module('plone.app.stagingbehavior.relation.StagingRelationValue', Dummy)
alias_module('plone.contentratings.assignment.LocalAssignmentUtility', LocalAssignmentUtility)
alias_module('plone.contentratings.interfaces.IUnratable', Interface)
alias_module('plone.formwidget.geolocation.geolocation.Geolocation', Dummy)
alias_module('plone.app.controlpanel.markup.WickedSettings', Dummy)
