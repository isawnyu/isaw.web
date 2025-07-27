from Acquisition import aq_inner
from plone.registry.interfaces import IRegistry
from zope.component import getUtility, getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

from ..interfaces import IISAWSettings


class SiteFooter(ViewletBase):
    render = ViewPageTemplateFile('footer.pt')

    def html(self):
        context = aq_inner(self.context)
        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        user_actions = context_state.actions('user')
        anonymous = portal_state.anonymous()

        actions_html = '<ul>'
        for action in user_actions:
            actions_html += '<li id="personaltools-{}">'.format(action['id'])
            actions_html += '<a href="{}">{}</a>'.format(action['url'],
                                                         action['title'])
            actions_html += '</li>'
        actions_html += '</ul>'

        if not anonymous:
            member = portal_state.member()
            userid = member.getId()

            homelink_url = "%s/useractions" % portal_state.navigation_root_url()
            membership = getToolByName(context, 'portal_membership')
            member_info = membership.getMemberInfo(userid)
            if member_info:
                fullname = member_info.get('fullname', '')
            else:
                fullname = None
            if fullname:
                username = fullname
            else:
                username = userid

            actions_html += '<p><img src="user.png" /> <em>{}</em></p>'.format(
                username)

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IISAWSettings, False)
        html = getattr(settings, 'footer_html', u'')
        html = html.replace('<ul id="personal-tools-links"></ul>', actions_html)

        self.actions_html = actions_html
        self.column_one = getattr(settings, 'column_one', u'')
        self.column_two = getattr(settings, 'column_two', u'')
        self.disclaimer = getattr(settings, 'disclaimer', u'')

        return html

