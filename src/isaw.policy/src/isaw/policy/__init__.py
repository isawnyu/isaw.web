# Disable the HomeFolderLocator from plone.app.iterate
import logging
from zope.i18nmessageid import MessageFactory
from . import patches

# XXX: Why did we disable home folder finding?
# from plone.app.iterate.containers import HomeFolderLocator
# HomeFolderLocator.available = False


# Set up the i18n message factory for our package
MessageFactory = MessageFactory('isaw.policy')

logger = logging.getLogger('isaw.policy')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    patches.patch_saml_login()


from plone.app.upgrade.utils import alias_module

class Geolocation(object):
    """dummy"""
    pass

alias_module('Products.Maps.adapters.Geolocation', Geolocation)
alias_module('plone.formwidget.geolocation.geolocation.Geolocation', Geolocation)