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





class Geolocation(object):
    """dummy"""
    pass

class ILocation(Interface):
    """dummy"""


# aliasing geolocation class to please the storage
alias_module('Products.Maps.adapters.Geolocation', Geolocation)
alias_module('plone.formwidget.geolocation.geolocation.Geolocation', Geolocation)
alias_module('isaw.policy.map_extender.ILocation', ILocation)