from DateTime import DateTime

from zope.interface import implementer

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from isaw.theme.browser.interfaces import IUtilsView
from isaw.theme.browser.interfaces import ISSOView
from isaw.policy.config import IS_PRODUCTION


@implementer(IUtilsView)
class UtilsView(BrowserView):
    """See `IUtilsView` for documentation
    """

    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        self.portal_catalog = getToolByName(context, 'portal_catalog')
        self.portal_root = getToolByName(context, 'portal_url')

    def getUpcomingEvents(self, limit=3):
        """Grabbing latests news stuff for the news landing page"""

        catalog = self.portal_catalog(portal_type=['Conference',
                                                'Exhibition',
                                                'Event',
                                                'General',
                                                'Lecture',
                                                'Performance',
                                                'Seminar',
                                                'Sponsored'],
                                   end={'query': DateTime(), 'range': 'min'},
                                   sort_on='start',
                                   review_state=['published',
                                                 'external'])[:limit]
        if catalog == []:
            return False
        else:
            return catalog

    def getNewsItems(self, limit=3):
        """Grabbing latests news stuff for the news landing page"""
        return self.portal_catalog(portal_type='News Item',
                                   sort_on='Date',
                                   sort_order='descending',
                                   review_state=['published',
                                                 'external'])[:limit]

    def getFeatured(self):
        """Grab the featured page object"""
        root = self.portal_root.getPortalObject()
        featured = getattr(root, "featured")
        body = featured.CookedBody()
        return body

    def getMonthName(self, month, full=None):
        """ Translates a month int into a short name """
        month_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL',
                      'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        full_month_list = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL',
                           'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER',
                           'OCTOBER', 'NOVEMBER', 'DECEMBER']
        if type(month) is int and 0 < month < 13:
            return full and full_month_list[month-1] or month_list[month-1]
        return ''

    def formatSiteMap(self, code):
        """ Customizes the sitemap pre-formated code to fit the comps """
        # we want to grab what's in the title attribute and drop it in a div after the element's link
        repeat = '</li>'
        summary_starts = 'title="'
        summary_stops = '"'
        insert_after = '</div>'
        for element in code.split(repeat):
            if summary_starts in element:
                summary = element.split(summary_starts)[1].split(summary_stops)[0]
                new_element = element.replace(insert_after,'%s<div class="sitemap-summary">%s</div>\
                    <div class="sitemap-gray">Dummy Gray Text, change me in theme egg, browser, \
                    utilsview.py</div>' % (insert_after, summary))
                code = code.replace(element, new_element)
        return code


@implementer(ISSOView)
class SSOView(BrowserView):
    """Makes URLs for SSO login/logout accible from restricted python.
    """

    dev_logout_url = 'https://shibbolethqa.es.its.nyu.edu/idp/profile/Logout'
    prod_logout_url = 'https://shibboleth.nyu.edu/idp/profile/Logout'

    def logout(self):
        self.request.response.redirect(self.logout_url)

    @property
    def logout_url(self):
        if self.is_prod:
            return self.prod_logout_url
        return self.dev_logout_url

    @property
    def is_prod(self):
        return IS_PRODUCTION
