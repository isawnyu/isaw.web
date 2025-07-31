from collective.z3cform.datagridfield.registry import DictRow
from zope import schema
from zope.interface import Interface


class INamedLocation(Interface):
    identifier = schema.ASCIILine(title=u"ID")
    title = schema.TextLine(title=u"Title")
    latitude = schema.ASCIILine(title=u"Latitude")
    longitude = schema.ASCIILine(title=u"Longitude")


class IISAWFacultyCVSettings(Interface):
    """Control panel settings"""

    named_locations = schema.List(
        title=u"Locations with names and lat/lng coordinates",
        value_type=DictRow(
            title=u"Location",
            schema=INamedLocation,
        )
    )
