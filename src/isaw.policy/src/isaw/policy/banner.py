from collective.behavior.banner.banner import IBanner
from plone.dexterity.content import Item
from zope.interface import implementer


@implementer(IBanner)
class ISAWBanner(Item):
    """ISAW Banner content type"""

    @property
    def title(self, ):
        return self.banner_title

    @title.setter
    def set_title(self, value):
        self.banner_title = value