from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implementer
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from isaw.theme.portlets.widget import ImageWidget

class IFeaturedPortlet(IPortletDataProvider):

    image = schema.Field(
            title=_(u'Featured Image'),
            description=_(u'A small image from the current feature'),
            required=False)

    featured_title = schema.TextLine(
            title=_(u'Title of Current Feature'),
            description=_(u'Title to appear on the front page about current feature.'),
            required=False)

    featured_description = schema.Text(
            title=_(u'Description of Current Feature'),
            description=_(u'Description of current feature as it will appear on the front page.'),
            required=False)

    featured_lefttext = schema.TextLine(
            title=_(u'The text that appears to the left of this portlet'),
            description=_(u'Text to appear on the left'),
            required=False)


@implementer(IFeaturedPortlet)
class Assignment(base.Assignment):

    header = u''
    image = None
    assignment_context_path = None

    def __init__(self,
                 image=None,
                 featured_title=None,
                 featured_description=None,
                 featured_lefttext=None,
                 header=None,
                 assignment_context_path=None):

        self.image = image
        self.featured_title = featured_title
        self.featured_description = featured_description
        self.featured_lefttext = featured_lefttext
        self.header = header
        self.assignment_context_path = assignment_context_path

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return _(u"Feature Portlet")

class Renderer(base.Renderer):

    render = ViewPageTemplateFile('feature.pt')

    def title(self):
        return self.data.featured_title

    def description(self):
        return self.data.featured_description

    def lefttext(self):
        return self.data.featured_lefttext

    @property
    def image_tag(self):
        if self.data.image:
            state=getMultiAdapter((self.context, self.request),
                               name="plone_portal_state")
            portal=state.portal()
            #assignment_url = \
            #     portal.unrestrictedTraverse(
            #  self.data.assignment_context_path).absolute_url()
            assignment_url = "isaw/++contextportlets++plone.rightcolumn"
            # width = self.data.image.width
            # height = self.data.image.height
            return "<img src='%s/%s/@@image' width='150' height='150' alt='%s'/>" % \
                 (assignment_url,
                 self.data.__name__,
                 self.data.featured_description)
        return None

class AddForm(base.AddForm):
    form_fields = form.Fields(IFeaturedPortlet)
    form_fields['image'].custom_widget = ImageWidget
    label = _(u"Add Featured Portlet")

    def create(self, data):
        assignment_context_path = \
                    '/'.join(self.context.__parent__.getPhysicalPath())
        return Assignment(assignment_context_path=assignment_context_path, **data)

class EditForm(base.EditForm):

    form_fields = form.Fields(IFeaturedPortlet)
    form_fields['image'].custom_widget = ImageWidget
    description = _(u"This portlet displays featured front page copy.")
