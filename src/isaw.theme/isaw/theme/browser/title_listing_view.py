from Products.Five.browser import BrowserView
from zope.interface import implementer

from isaw.theme.browser.interfaces import ITitleListingView


@implementer(ITitleListingView)
class TitleListingView(BrowserView):
    """view class"""
    batch_size = 0
    page = 1

    def __init__(self, request, context):
        super(TitleListingView, self).__init__(request, context)
        self.page = int(self.request.get('page', 1))

    def _query(self, query=None, exclude=None, b_start=None, b_size=None):
        if b_size is None:
            b_size = self.batch_size
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
            query['sort_on'] = 'getObjPositionInParent'
            query['sort_order'] = 'ascending'
            items = self.context.getFolderContents(contentFilter=query,
                                                   batch=True, b_size=b_size)
        elif self.context.portal_type == 'Collection':
            items = self.context.results(True, b_start, b_size,
                                         custom_query=query)
        else:
            items = []

        return items

    def listings(self, b_start=None, b_size=None):
        """get a page of listings"""
        return self._query(b_start=b_start, b_size=b_size)

    @property
    def alumni_vrs_map(self, ):
        request = self.request
        if 'alumni' in request.get('URL0'):
            return 'alumni'
        if 'visiting-research-scholars' in request.get('URL0'):
            return 'vrs'
        return ''