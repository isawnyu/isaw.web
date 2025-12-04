from Products.Five.browser import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

# facultycv requires the pisa module for pdf view
import ho.pisa as pisa


class ProfileView(BrowserView):
    pass


class PdfView(BrowserView):
    """ pdf view"""

    def __call__(self):
        response = self.request.response
        title = self.context.Title()
        ftitle = "/tmp/%s_CV.pdf" % (title)
        filename = ftitle

        attachment = 'attachment; filename=%s' % (ftitle)
        f = file(filename, "wb")
        pdf_template = ViewPageTemplateFile('templates/pdf-view.pt')(self)

        response.setHeader('Content-Type', 'application/pdf')
        response.setHeader('Content-Disposition', attachment)
        pdf = pisa.CreatePDF(pdf_template.encode("UTF-8"), response)
        f.flush()
        f.close()

        if not pdf.err:
            return response
        else:
            # Something is wrong
            # Fledge this out later
            pass


class PeopleView(BrowserView):

    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        self.portal_catalog = getToolByName(context, 'portal_catalog')

    def getFacultyList(self, limit=10):
        return self.portal_catalog(portal_type='Profile',
                                   review_state='external')[:limit]


class MemberProfile(BrowserView):

    def profile_for(self, userid):
        membership = getToolByName(self.context, 'portal_membership')
        member = membership.getMemberById(userid)
        if member is None:
            return
        profile_uid = member.getProperty('ProfileReference')
        if profile_uid:
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog(UID=profile_uid)
            if brains:
                return {
                    'title': brains[0].Title,
                    'url': brains[0].getURL(),
                }
