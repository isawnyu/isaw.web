# -*- coding: utf-8 -*-
"""a simple portlet to display the image from a news item"""
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


class IEventDetailPortlet(IPortletDataProvider):
    """data provider, no fields required"""
    pass


@implementer(IEventDetailPortlet)
class Assignment(base.Assignment):
    """simple portlet assignment"""

    @property
    def title(self):
        return u"Event Detail Portlet"


class Renderer(base.Renderer):

    @property
    def available(self):
        is_event = self.context.portal_type == 'Event'
        return is_event

    render = ViewPageTemplateFile('eventdetail.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
