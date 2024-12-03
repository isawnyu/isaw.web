try:
    from plone.app.search.browser import Search, SortOption, _
except ImportError:
    from Products.CMFPlone.browser.search import Search, SortOption, _

class ISAWSearch(Search):
    """Customize sort options"""

    def sort_options(self):
        """ Sorting options for search results view. """
        return (
            SortOption(self.request, _(u'relevance'), ''),
            SortOption(
                self.request, _(u'date (newest first)'),
                'Date', reverse=True
            ),
        )
