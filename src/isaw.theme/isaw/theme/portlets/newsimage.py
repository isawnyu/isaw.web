# -*- coding: utf-8 -*-
"""a simple portlet to display the image from a news item"""
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


class INewsItemImagePortlet(IPortletDataProvider):
    """data provider, no fields required"""
    pass


@implementer(INewsItemImagePortlet)
class Assignment(base.Assignment):
    """simple portlet assignment"""

    @property
    def title(self):
        return u"News Item Image Portlet"


class Renderer(base.Renderer):

    #def update(self, ):
        #self.has_image = getattr(self.context, 'image', None) is not None

    @property
    def available(self):
        is_news = self.context.portal_type == 'News Item'
        self.has_image = getattr(self.context, 'image', None) is not None

        return is_news and self.has_image

    render = ViewPageTemplateFile('newsimage.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
