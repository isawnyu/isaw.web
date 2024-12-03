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

    @property
    def available(self):
        is_news = self.context.portal_type == 'News Item'
        has_image = self.context.getImage()
        return is_news and has_image

    render = ViewPageTemplateFile('newsimage.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
