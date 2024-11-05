"""Main product initializer
"""

from zope.i18nmessageid import MessageFactory
from isaw.facultycv import config

from Products.CMFCore import utils

# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

facultycvMessageFactory = MessageFactory('isaw.facultycv')


def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    """
