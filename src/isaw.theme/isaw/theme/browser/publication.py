from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from urllib.parse import urlparse

class PublicationView(BrowserView):
    """view class"""

    @staticmethod
    def url_domain(url):
        host = urlparse(url).hostname
        parts = host.split('.')
        domain = []

        for part in reversed(parts):
            if part in ('www', 'api'):
                continue
            domain.insert(0, part)
            if len(domain) >= 2 and len(part) > 3:
                break

        return '.'.join(domain)

    @property
    def authors(self):
        members = self._get_members(self.context.authors)
        return ', '.join(members)

    @property
    def contributors(self):
        members = self._get_members(self.context.contributors)
        return ', '.join(members)

    @property
    def editors(self):
        members = self._get_members(self.context.editors)
        return ', '.join(members)

    def _get_members(self, member_list):
        mt = getToolByName(self.context, 'portal_membership')
        members = []
        for author in member_list:
            author = author.strip()
            if not author:
                continue
            info = mt.getMemberInfo(author)
            if info:
                members.append('<a href="%s">%s</a>' % (info.get('home_page'),
                               info.get('fullname', author)))
            else:
                members.append(author)
        return members

    @property
    def images(self):
        return self.context.objectValues()


class PublicationImagesView(BrowserView):
    """ images overlay """

    @property
    def images(self):
        return self.context.objectValues()


class PublicationListingView(BrowserView):
    """view class"""
    batch_size = 0
    page = 1

    def __init__(self, request, context):
        super(PublicationListingView, self).__init__(request, context)
        self.page = int(self.request.get('page', 1))

    def _query(self, query=None, exclude=None, b_start=None, b_size=None):
        if b_size is None:
            b_size = self.batch_size
        if b_start is None:
            b_start = (getattr(self, 'page', 1) - 1) * b_size

        if query is None:
            query = {'portal_type': 'isaw.policy.publication'}

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
                                                   batch=True, b_size=b_size)
        elif self.context.portal_type == 'Topic':
            if b_start and not self.request.get('b_start'):
                self.request['b_start'] = b_start
            items = self.context.queryCatalog(self.request, True, b_size,
                                              **query)
        elif self.context.portal_type == 'Collection':
            items = self.context.results(True, b_start, b_size,
                                         custom_query=query)
        else:
            items = []

        return items

    def listings(self, b_start=None, b_size=None):
        """get a page of listings"""
        return self._query(b_start=b_start, b_size=b_size)