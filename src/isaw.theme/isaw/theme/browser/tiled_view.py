# -*- coding: utf-8 -*-
"""View providing a tiled layout for listed items

Suitable for folders or collections

Also includes a viewlet which will show the "featured_item" returned by
the method on the view.
"""
from DateTime import DateTime
from plone.app.layout.viewlets import common as base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from plone.memoize import view

from isaw.theme.browser.interfaces import ITiledListingView


STICKY_TAGS = ['featured', 'Featured', 'FEATURED']
IMAGE_FIELDS = ['image', 'leadImage']


class TileDetailsMixin(object):

    _translation_service = None
    _membership_tool = None

    @property
    def translation_service(self):
        if self._translation_service is None:
            self._translation_service = getToolByName(
                self.context, 'translation_service'
            )
        return self._translation_service

    @property
    def membership_tool(self):
        if self._membership_tool is None:
            self._membership_tool = getToolByName(
                self.context, 'portal_membership'
            )
        return self._membership_tool

    def get_byline(self, brain):
        # Only news items show bylines in tiled listings
        if brain.portal_type != 'News Item':
            return
        creator = brain.Creator
        if callable(creator):
            creator = creator()
        author_info = self.membership_tool.getMemberInfo(creator)
        author = ''
        if author_info:
            author = author_info.get('fullname') or author_info.get('username')
        if not author:
            author = creator
        parts = [author]

        date = brain.Date
        if callable(date):
            date = date()
        if date == 'None':
            date = None

        if date:
            parts.append(self.translation_service.ulocalized_time(
                DateTime(date), None, None, self.context
            ))
        return "by " + " | ".join(parts)

    def get_image(self, brain):
        tag = self.image_placeholder
        scales = self.context.restrictedTraverse(brain.getPath() + '/@@images')
        title = brain.Title
        if callable(title):
            title = title()
        # attempt to find any image field on the object, using know field names
        # TODO: this would be a nice place for some configuration.
        for field in IMAGE_FIELDS:
            try:
                scale = scales.scale(field, self.image_scale)
            except AttributeError:
                scale = None
            if scale is not None:
                tag = scale.tag(alt=title, title=title)
                break
        return tag


class TiledListingView(BrowserView, TileDetailsMixin):
    """view class"""
    implements(ITiledListingView)
    image_scale = 'blogtile'
    image_placeholder = '<div class="blogtile_placeholder">&nbsp;</div>'
    batch_size = 9
    page = 1

    def __init__(self, request, context):
        super(TiledListingView, self).__init__(request, context)
        self.page = int(self.request.get('page', 1))

    def _query(self, query=None, exclude=None, b_start=None, b_size=None):
        batch = True
        if b_size is None:
            b_size = self.batch_size
        elif b_size == 0:
            b_size = None
            batch = False
        if b_start is None:
            b_start = (getattr(self, 'page', 1) - 1) * b_size

        if query is None:
            query = {}

        if exclude is not None:
            uuid = getattr(exclude, 'UID')
            if callable(uuid):
                uuid = uuid()
            if uuid:
                query['UID'] = {'not': uuid}

        if self.context.portal_type == 'Folder':
            self.request['b_start'] = b_start
            self.request['b_size'] = b_size
            query['b_start'] = b_start
            query['b_size'] = b_size
            items = self.context.getFolderContents(contentFilter=query,
                                                   batch=batch, b_size=b_size)
        elif self.context.portal_type == 'Topic':
            if b_start and not self.request.get('b_start'):
                self.request['b_start'] = b_start
            items = self.context.queryCatalog(self.request, batch, b_size,
                                              **query)
        elif self.context.portal_type == 'Collection':
            items = self.context.results(batch, b_start, b_size,
                                         custom_query=query)
        else:
            items = []

        return items

    def listings(self, b_start=None, b_size=None):
        """get a page of listings"""
        return self._query(exclude=self.featured_item(), b_start=b_start,
                           b_size=b_size)

    @view.memoize
    def featured_item(self):
        """get the 'featured item' for the listing
        """
        featured = None
        batch = self._query(query={'Subject': STICKY_TAGS,
                                   'sort_on': 'Date',
                                   'sort_order': 'reverse'},
                            b_start=0, b_size=1)
        items = [i for i in batch]
        if len(items) > 0:
            featured = items[0]
        return featured


class SimpleTiledListingView(TiledListingView):

    def listings(self):
        """get a page of listings"""
        return self._query(exclude=self.featured_item(), b_start=0,
                           b_size=0)


class FeaturedItemViewlet(base.ViewletBase, TileDetailsMixin):
    index = ViewPageTemplateFile('templates/featured_item.pt')
    image_scale = 'featured'
    image_placeholder = '<div class="featured_placeholder">&nbsp;</div>'

    def update(self):
        self.show = (ITiledListingView.providedBy(self.view) and
                     self.view.featured_item() is not None)

    def get_item(self):
        return self.view.featured_item()
