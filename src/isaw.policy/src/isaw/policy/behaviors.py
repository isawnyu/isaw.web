# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.contenttypes import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from zope.interface import invariant
from zope.interface import Invalid

class MissingAltText(Invalid):
    """Missing alt text Exception
    """

IMAGE_ALT_FIELD_NAME = 'image_alt'


@provider(IFormFieldProvider)
class IEventISAWBehavior(model.Schema):
    """Behavior for event fields"""

    subtitle = schema.TextLine(
        title=u"Subtitle",
        required=False,
    )

    eventType = schema.Choice(
        title=u"Event Type",
        description=u"Select the most appropriate term to "
                        "describe the nature of this event.",
        vocabulary="isaw.vocabulary.eventTypes",
        required=True,
    )

    speaker = schema.TextLine(
        title=u"Speaker",
        description=u"If this event features a single speaker, "
                                   u"enter their name in this field.",
        required=False,
    )

    speakerAffiliation = schema.TextLine(
        title=u"Speaker Affiliation",
        description=u"If this event features a single speaker, enter "
                                   u"their institutional affilication in this field.",
        required=False,
    )

    rsvpRequired = schema.Bool(
        title=u"RSVP Required",
        description=u"If an RSVP is required, check this box.",
        required=False,
    )



@provider(IFormFieldProvider)
class INewsLeadImageISAWBehavior(ILeadImage):

    alt = schema.TextLine(
        title=_(u'label_leadimage_alt', default=u'Lead Image Alt Text'),
        description=_(u'help_leadimage_alt', default=u"Accessibility guidelines require an alt text"),
        required=False,
    )

    @invariant
    def validate_alt_image(data):
        upload = getattr(data, 'image', None)
        alt = getattr(data, 'alt', None)

        if upload and not alt:
            raise MissingAltText(_(u"missing_alt_text",
                default=u"Alt text is required when uploading an image"))



@implementer(INewsLeadImageISAWBehavior)
@adapter(IDexterityContent)
class ISAWNewsLeadImage(object):

    def __init__(self, context):
        self.context = context
