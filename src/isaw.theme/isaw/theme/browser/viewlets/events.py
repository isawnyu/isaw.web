from Acquisition import aq_inner
from plone.registry.interfaces import IRegistry
from zope.component import getUtility, getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.contenttypes.behaviors.viewlets import LeadImageViewlet as DefaultLeadImageViewlet

from ..interfaces import IISAWSettings


class SearchEvents(ViewletBase):
    render = ViewPageTemplateFile('events.pt')

    def is_event_listing(self):
        return self.view.__name__ == 'event-listing'


class LeadImageWithCaptionViewlet(DefaultLeadImageViewlet):
    index = ViewPageTemplateFile('event_view_leadimage.pt')

    def render(self):
        return self.index()
