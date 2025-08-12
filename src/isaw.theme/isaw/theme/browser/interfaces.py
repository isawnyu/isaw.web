# -*- coding: utf-8 -*-
from plone.supermodel import model
from plone.theme.interfaces import IDefaultPloneLayer
from zope import schema
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager
from isaw.policy import MessageFactory as _

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """


class ILeftCol(IViewletManager):
    """A viewlet manager that sits in the left most column of the page
       (an addition to the main template)
    """


class IUtilsView(Interface):
    """ Marker interface for misc browser view """

    def getUpcomingEvents(limit):
        """Grabbing upcoming events for the home page"""

    def getMonthName(self, month):
        """ Translates a month int into a short name """

    def formatSiteMap(self, code):
        """ Customizes the sitemap pre-formated code to fit the comps """


class ISSOView(Interface):
    """View for interacting with NYU SSO"""

    def logout():
        """Redirect to a staging or production URL at NYU.
        """


class ITiledListingView(Interface):
    """marker interface for a view providing tiled view listed items

    This view is suitable for folders or collections
    """


class ITitleListingView(Interface):
    """marker interface for a view providing listing by title only

    This view is suitable for folders or collections
    """


class IEventListingView(Interface):
    """marker interface for a view providing one column listed items

    This view is suitable for folders or collections
    """


class IBibliographicListingView(Interface):
    """marker interface for a view providing list of bibliographic items

    This view is suitable for folders or collections
    """


DEFAULT_FOOTER_HTML = u"""<div class="contact footer-portlet">
<h3>Contact</h3>
<p>15 East 84th St.<br />New York, NY 10028<br />212-992-7800<br /> <a href="mailto:isaw@nyu.edu">isaw@nyu.edu</a></p>
</div>
<div class="support footer-portlet" id="footer-support">
<h3 class="support"><a href="support-isaw" id="footer-support-link">Support ISAW</a></h3>
<ul id="personal-tools-links"></ul>
</div>
<div class="hours footer-portlet">
<h3>Gallery Hours</h3>
<p>The galleries are currently closed.</p>
</div>
<div class="hours footer-portlet">
<h3>Library Hours</h3>
<p><strong>Mon-Fri</strong> 9am-6pm</p>
</div>
"""

class IISAWSettings(Interface):
    emergency_message = schema.Text(title=u"Emergency Message",
            description=u"Any text here will be displayed at the top of the site. An empty field means do not display emergency message",
            required=False)

    no_results_message = schema.Text(title=u'No results message for event search',
            default=u'<p>There are no upcoming events.</p>')

    footer_html = schema.Text(title=u"Footer HTML (deprecated)",
            description=u"The full HTML of the site footer (deprecated)",
            required=True,
            default=DEFAULT_FOOTER_HTML)

    column_one = schema.Text(
        title=u"Column One",
        description=u"HTML content for the first footer column.",
        required=False,
        missing_value='',
    )

    column_two = schema.Text(
        title=u"Column Two",
        description=u"HTML content for the second footer column.",
        required=False,
        missing_value='',
    )

    disclaimer = schema.Text(
        title=u"Disclaimer",
        description=u"HTML content for the footer disclaimer.",
        required=False,
        missing_value='',
    )

    model.fieldset(
          'Footer',
          label=_(u"Footer settings"),
          fields=['footer_html', 'column_one', 'column_two', 'disclaimer']
      )
