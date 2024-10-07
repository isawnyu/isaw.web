# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider


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
