# -*- coding: utf-8 -*-
from ..interfaces import IISAWSettings
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.textfield.value import RichTextValue
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class EmergencyMessage(ViewletBase):
    render = ViewPageTemplateFile('emergency.pt')

    def message(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IISAWSettings, False)
        message = getattr(settings, 'emergency_message', u'')
        closed = self.request.cookies.get("isaw-emergency-read", None)
        if not message or closed:
            message = u''
        if isinstance(message, RichTextValue):
            message = message.raw

        return message.strip()
