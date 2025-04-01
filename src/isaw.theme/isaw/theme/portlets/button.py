# -*- coding: utf-8 -*-
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.formlib import form
from zope.interface import implementer


class IButtonPortlet(IPortletDataProvider):

    text = schema.TextLine(
        title=_(u'Link Text'),
        description=_(u'The text that will display inside the button.'),
    )

    url = schema.TextLine(
        title=_(u'URL'),
        description=_(u'The target URL for the link.'),
    )


@implementer(IButtonPortlet)
class Assignment(base.Assignment):
    """simple portlet assignment"""

    @property
    def title(self):
        return u"Button Portlet"

    def __init__(self, text=None, url=None):
        self.text = text
        self.url = url


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('button.pt')

    def text(self):
        return self.data.text

    def url(self):
        return self.data.url


class AddForm(base.AddForm):
    schema = IButtonPortlet
    form_fields = form.Fields(IButtonPortlet)
    label = _(u"Add Button Portlet")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    schema = IButtonPortlet
    form_fields = form.Fields(IButtonPortlet)
