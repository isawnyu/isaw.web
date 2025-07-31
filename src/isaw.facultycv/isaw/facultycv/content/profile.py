"""Definition of the profile content type
"""
import re
from urlparse import urlparse
from zope.interface import implements

from plone import api as plone_api
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from isaw.facultycv.interfaces import Iprofile
from isaw.facultycv.config import PROJECTNAME

profileSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.ImageField(
        name='Image',
        sizes=None,
        widget=atapi.ImageWidget(
            label=u'Profile Image',
            label_msgid='isaw.facultycv_label_ProfileImage',
            il8n_domain='isaw.facultycv',
        ),
        required=False,
        searchable=True,
        accessor='profileImage',
    ),

    atapi.ReferenceField(
        name='ProfileRef',

        widget=atapi.ReferenceWidget(
            label=u'Profile reference',
        ),
        relationship='owned_profile',
        multiValued=False,
    ),

    atapi.TextField(
        name='Titles',
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label=u'Faculty Titles',
            label_msgid='isaw.facultycv_label_Titles',
            il8n_domain='isaw.facultycv',
        ),

        required=False,
        searchable=True
    ),

    atapi.StringField(
        name='pronouns',
        widget=atapi.StringWidget(
            label=u'Pronouns',
            label_msgid='isaw.facultycv_label_Pronouns',
            il8n_domain='isaw.facultycv',
        ),
        required=False,
        searchable=False
    ),

    atapi.StringField(
        name='Phone',
        default_output_type='text/x-html-safe',
        widget=atapi.StringWidget(
            label=u'Phone',
            label_msgid='isaw.facultycv_label_Phone',
            il8n_domain='isaw.facultycv',
        ),

        required=False,
        searchable=True

    ),

    atapi.StringField(
        name='Email',
        default_output_type='text/x-html-safe',
        widget=atapi.StringWidget(
            label=u'Email',
            label_msgid='isaw.facultycv_label_Email',
            il8n_domain='isaw.facultycv',
        ),

        required=False,
        searchable=True

    ),

    atapi.StringField(
        name='Address',
        default_output_type='text/x-html-safe',
        widget=atapi.StringWidget(
            label=u'Address Information',
            label_msgid='isaw.facultycv_label_Address',
            il8n_domain='isaw.facultycv',
        ),

        required=False,
        searchable=True

    ),

    atapi.TextField(
        name='Profile Blurb',
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label=u'Profile Blurb',
            label_msgid='isaw.facultycv_label_Profile',
            il8n_domain='isaw.facultycv',
        ),

        required=False,
        searchable=True
    ),

    atapi.LinesField(
        name='ExternalURIs',
        required=False,
        widget=atapi.LinesWidget(
            label=u'External URIs (e.g. VIAF, Facebook, GitHub, etc.)',
            label_msgid='isaw.facultycv_label_external_uris',
            il8n_domain='isaw.facultycv',
        ),
    ),

    atapi.StringField(
        name='MemberID',
        vocabulary_factory="isaw.facultycv.Users",
        enforceVocabulary=True,
        widget=atapi.SelectionWidget(
            label=u'Associated Member ID',
            label_msgid='isaw.facultycv_label_MemberID',
            il8n_domain='isaw.facultycv',
        ),
        required=False,
    ),

    atapi.StringField(
        name='NamedLocation',
        vocabulary_factory="isaw.facultycv.named_locations",
        enforceVocabulary=True,
        widget=atapi.SelectionWidget(
            label=u'Location',
            label_msgid='isaw.facultycv_label_Location',
            il8n_domain='isaw.facultycv',
        ),
        required=False,
    ),

))

profileSchema['title'].storage = atapi.AnnotationStorage()
profileSchema['description'].storage = atapi.AnnotationStorage()

profileSchema['description'].widget.visible = {"edit": "invisible"}
profileSchema['ProfileRef'].widget.visible = {"edit": "invisible"}


schemata.finalizeATCTSchema(
    profileSchema,
    folderish=True,
    moveDiscussion=False
)

DOMAIN_LINK_MAP = {
    'facebook.com': {
        "title": "Facebook: {user}",
    },
    'academia.edu': {
        "title": "Academia.edu: {user}",
    },
    'doodle.com': {
        "title": "Doodle Calendar: {user}",
    },
    'linkedin.com': {
        "title": "LinkedIn: {user}",
    },
    'orcid.org': {
        "title": "ORCID: {user}"
    },
    'github.com': {
        "title": "GitHub: {user}",
        "regexps": [r'^https?://github.com/(?P<id>[^/]+).*$'],
    },
    'hcommons.org': {
        "title": "Humanities Commons: {user}",
        "regexps": [r'^https?://hcommons.org/members/(?P<id>[^/]+).*$'],
    },
    'twitter.com': {
        "title": "Twitter: {user}",
        "regexps": [r'^https?://twitter\.com/(?P<id>[^/]+).*$'],
    },
    'viaf.org': {
        "title": "VIAF: {user}",
        "regexps": [r'^https?://viaf\.org/viaf/(?P<id>[^/]+).*$'],
    },
    'wikipedia.org': {
        "title": "Wikipedia: {user}",
        "regexps": [r'^https?://[^/]+\.wikipedia\.org/wiki/User:(?P<id>[^/]+).*$',
                    r'^https?://[^/]+\.wikipedia\.org/wiki/(?!User:)(?P<id>[^/]+).*$'],
    },
    'zotero.org': {
        "title": "Zotero: {user}",
        "regexps": [r'^https?://www\.zotero\.org/(?P<id>[^/]+).*$'],
    },
}


class profile(folder.ATFolder):
    """Profile"""
    implements(Iprofile)

    meta_type = "Profile"
    schema = profileSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    @property
    def named_location(self):
        """Return the full named location dict from the registry for this profile's NamedLocation identifier, or None."""
        identifier = self.getNamedLocation()
        if not identifier:
            return None
        record_name = "isaw.facultycv.interfaces.settings.IISAWFacultyCVSettings.named_locations"
        items = plone_api.portal.get_registry_record(record_name) or []
        for loc in items:
            if loc.get("identifier") == identifier:
                return loc
        return None

    def profile_links(self):
        links = self.getExternalURIs() or []
        results = []
        fullname = self.Title()
        for link in links:
            parsed = urlparse(link)
            if parsed.hostname is None:
                continue
            info = {'link': link, 'text': link}
            results.append(info)
            user = fullname
            host = '.'.join(parsed.hostname.split('.')[-2:])
            domain_info = DOMAIN_LINK_MAP.get(host)
            if not domain_info:
                link_parts = link.split('|')
                if len(link_parts) > 1:
                    info['link'] = link_parts[0]
                    info['text'] = link_parts[1]
                continue
            text = domain_info['title']
            for pattern in domain_info.get('regexps', ()):
                match = re.match(pattern, link)
                if not match:
                    continue
                groups = match.groups()
                if groups:
                    user = groups[0]
                    break
            info['text'] = text.format(user=user)
        return results

atapi.registerType(profile, PROJECTNAME)
