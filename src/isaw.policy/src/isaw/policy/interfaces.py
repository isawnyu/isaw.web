from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema import List, Text, TextLine, Tuple, URI
from isaw.policy import MessageFactory as _
from plone.app.textfield import RichText
from plone.dexterity.browser import add
from plone.supermodel import model
from plone.namedfile import field as namedfile
from z3c.form.browser.textlines import TextLinesFieldWidget
from plone.autoform import directives

class IISAWPolicyLayer(Interface):
    """Marker layer interface for ISAW Site"""


class IISAWPublication(model.Schema):
    title = TextLine(
        title=_(u"Short Title"),
        description=_(u"The short title of this publication"),
    )

    full_title = TextLine(
        title=_(u'Full Title'),  # Legacy attribute name is unfortunate. Sorry!
        description=_(u'The full bibliographic title of the publication'),
    )

    bibliographic_uri = URI(
        title=_(u"Zotero URI"),
        description=_(u"This is a URI to a Zotero bibliographic reference."),
        required=False,
    )

    description = Text(
        title=_(u'Summary'),
        description=_(u'Used in item listings and search results.'),
        required=False,
        missing_value=u'',
    )

    tag_line = TextLine(title=_(u'Tag Line'), required=False)

    authors = Tuple(
        title=_(u'Authors'),
        description=_(u'Enter username or plain-text name, one per line'),
        value_type=TextLine(),
        required=False,
        missing_value=(),
    )

    editors = Tuple(
        title=_(u'Editors'),
        description=_(u'Enter username or plain-text name, one per line'),
        value_type=TextLine(),
        required=False,
        missing_value=(),
    )

    contributors = Tuple(
        title=_(u'Contributors'),
        description=_(u'Enter username or plain-text name, one per line'),
        value_type=TextLine(),
        required=False,
        missing_value=(),
    )

    parent_title = TextLine(title=_(u'Parent Title'), required=False)

    parent_uri = URI(title=_(u'Parent URI'), required=False)

    volume = TextLine(title=_(u'Volume'), required=False)

    date_of_publication = TextLine(
        title=_(u'Publication Date'),
        description=_(u'Enter the date on which this publication was issued'),
        required=False)

    range = TextLine(
        title=_(u"Range"),
        required=False,
    )

    formatted_citation = RichText(
        title=_(u'Formatted Citation'),
        default_mime_type='text/html',
        allowed_mime_types=('text/html',),
        output_mime_type='text/x-html-safe',
        required=False,
    )

    worldcat_uri = URI(
        title=_(u"Worldcat URI"),
        description=_(u"This is a URI to access the identified resource."),
        required=False,
    )

    publisher = TextLine(title=_(u'Publisher'),
                         required=False)

    publisher_uri = URI(title=_(u'Publisher URI'),
                        required=False)

    extent = TextLine(title=_(u'Extent'),
                         required=False)

    access_uris = List(title=_(u'Access URIs (one per line)'),
                        value_type=URI(title=u'URI'),
                        required=False)
    directives.widget('access_uris', TextLinesFieldWidget)

    review_uris = List(title=_(u'Review URIs (one per line)'),
                        value_type=URI(title=u'URI'),
                        required=False)
    directives.widget('review_uris', TextLinesFieldWidget)

    order_uris = List(title=_(u'Order URIs (one per line)'),
                        value_type=URI(title=u'URI'),
                        required=False)
    directives.widget('order_uris', TextLinesFieldWidget)


    image = namedfile.NamedBlobImage(
        title=_(u'label_leadimage', default=u'Lead Image'),
        description=_(u'help_leadimage', default=u''),
        required=False,
    )

    alt = TextLine(
        title=_(u'label_leadimage_alt', default=u'Lead Image Alt Text'),
        description=_(u'help_leadimage_alt', default=u''),
        required=False,
    )

    image_caption = TextLine(
        title=_(u'label_leadimage_caption', default=u'Lead Image Caption'),
        description=_(u'help_leadimage_caption', default=u''),
        required=False,
    )

    isbn = TextLine(title=_(u'ISBN'),
                    required=False)

    issn = TextLine(title=_(u'ISSN'),
                    required=False)

    doi = TextLine(title=_(u'DOI'),
                   required=False)

    text = RichText(
        title=_(u'Body'),
        default_mime_type='text/html',
        allowed_mime_types=('text/html',),
        output_mime_type='text/x-html-safe',
        required=False,
    )

    @invariant
    def alt_text_invariant(data):
        if data.image and not data.alt:
            raise Invalid(_(u'Alt text is required for images'))


class PublicationAddForm(add.DefaultAddForm):
    portal_type = 'isaw.policy.publication'


class PublicationAddView(add.DefaultAddView):
    form = PublicationAddForm


class IISAWLibCollection(model.Schema):

    title = TextLine(
        title=_(u"Title"),
        description=_(u"The title of the Library Collection."),
    )

    id = TextLine(title=_(u'Short Title'))

    description = Text(
        title=_(u'Summary'),
        description=_(u'Used in item listings and search results.'),
        required=False,
        missing_value=u'',
    )

    image = namedfile.NamedBlobImage(
        title=_(u'label_leadimage', default=u'Lead Image'),
        description=_(u'help_leadimage', default=u''),
        required=False,
    )

    query_string = Text(
        title=_(u'NYU Library Catalog Query'),
        description=_(u'help_query_string', default=u''),
    )

    text = RichText(
        title=_(u'Body'),
        default_mime_type='text/html',
        allowed_mime_types=('text/html',),
        output_mime_type='text/x-html-safe',
        required=False,
    )
