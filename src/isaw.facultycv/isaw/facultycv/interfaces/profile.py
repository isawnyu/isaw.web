from collective import dexteritytextindexer
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope import schema

from isaw.facultycv import _


class IProfile(model.Schema):
    """Faculty Profile"""

    profileImage = NamedBlobImage(
        title=_("Profile Image"),
        required=False,
    )

    titles = RichText(title=_("Faculty Titles"), required=False)
    pronouns = schema.TextLine(title=_("Pronouns"), required=False)
    phone = schema.TextLine(title=_("Phone"), required=False)
    email = schema.TextLine(title=_("Email"), required=False)
    address = schema.TextLine(title=_("Address Information"), required=False)
    profile_blurb = RichText(title=_("Profile Blurb"), required=False)
    external_links = schema.List(
        title=_("External URIs (e.g. VIAF, Facebook, GitHub, etc.)"),
        required=False,
        value_type=schema.TextLine(),
    )
    user_id = schema.Choice(
        title=_("Associated Member ID"),
        required=False,
        vocabulary="isaw.facultycv.Users",
    )

    model.fieldset(
        "categorization", label=_("Categorization"), fields=("named_location",)
    )
    named_location = schema.Choice(
        title=_("Location"),
        vocabulary="isaw.facultycv.named_locations",
        required=False,
    )

    dexteritytextindexer.searchable(
        "titles", "phone", "email", "address", "profile_blurb"
    )


# xxx hide description and location

Iprofile = IProfile  # for backward compatibility
